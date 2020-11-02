# -*- coding: utf-8 -*-
import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'

import os
import logging
import xlrd
from douyin.tasks.dyuser import *
from douyin.tasks.models import *
from douyin.tasks.utils import *
from douyin.tasks.consumers import AckMessageConsumer
from douyin.tasks.producers import SyncMessageProducer
# from douyin.utils.hubservice import Hubservice

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
                    format='%(asctime)s %(name)s[%(process)d] %(levelname)s> %(message)s')
LOG = logging.getLogger('ImportConsumer')

class ImportMessageConsumer(AckMessageConsumer):

    exchange_name = 'douyin-app_import_message_exchange'
    queue_name = 'douyin-app_import_message'
    routing_key = 'douyin-app_import_message'
    consumer_tag = 'douyin-app_import_message_consumer'

    def __init__(self, configs=None):
        self.configs = configs

    def run(self):
        """docstring for run"""
        LOG.info('Sync Message Consumer is started...')
        self.consume(self.configs['amqp'])
        LOG.info('Sync Message Consumer is stopped')

    def handle_msg(self, msg):
        dept_id = msg.get('dept_id', 0)
        import_id = msg.get('import_id', 0)
        admin_import = AdminImport.find(import_id)

        if admin_import is None:
            return

        if int(dept_id) != int(admin_import.dept_id):
            return

        admin_import.status = 5
        admin_import.save()

        LOG.debug('handle msg: %s' % str(msg))
        func = getattr(self, 'handle_%s' % (admin_import.handle))
        if func is None:
            LOG.warn('func handle not found: %s' % (admin_import.handle,))
            return

        try:
            filepath = func(admin_import)
            if filepath:
                admin_import.status = Utils.STATUS_SUCCESS
                admin_import.save()
                os.remove(filepath)
                print '导入成功!!!'
        except Exception, e:
            admin_import.status = Utils.STATUS_ERROR
            admin_import.save()
            LOG.error('handle_%s error: %s' % (admin_import.handle, str(e)))


    def handle_keyword_file(self, admin_import):
        filepath = '%s%s' % (self.configs['web_path'], admin_import.filepath)
        print filepath

        book = xlrd.open_workbook(filepath)
        sheet = book.sheets()[0]
        rows = sheet.nrows

        if rows == 0:
            return filepath

        for rownum in range(1, rows):

            line = sheet.row_values(rownum)
            if not line:
                continue

            word_category = Utils.get_keyword_cates(line[1].strip())
            word_level = Utils.get_keyword_levels(line[2].strip())
            try:
                dept_id = admin_import.dept_id
                data = {
                    'dept_id': dept_id,
                    'word_subject': line[0],
                    'word_category': word_category,
                    'word_level': word_level,
                    'admin_id': dept_id
                }

                keyword = Keyword.where('word_subject', '=', line[0]).where('dept_id', '=', dept_id).first()
                if not keyword:
                    keyword = Keyword(data)
                    keyword.save()
                else:
                    keyword = Keyword.find(keyword.id)
                    for k, v in data.items():
                        setattr(keyword, k, v)
                    keyword.save()
            except Exception, e:
                LOG.error(e)

        producer = SyncMessageProducer(self.configs['amqp'])
        producer.produce({'model': 'Keyword', 'operate': 'sync'})
        producer.close()
        return filepath

    def handle_users_file(self, admin_import):
        filepath = '%s%s' % (self.configs['web_path'], admin_import.filepath)
        print filepath

        data = xlrd.open_workbook(filepath)
        table = data.sheets()[0]
        nrows = table.nrows

        if nrows == 0:
            return filepath

        for rownum in range(1, nrows): # start 1 skip table head
            row = table.row_values(rownum)
            if not row:
                continue
            try:
                dept_id = admin_import.dept_id
                data = {
                    'unique_id': row[0],
                    'dept_id': dept_id,
                    'type': dyusers.get_type(row[1]),
                    'tag_id': dyusers.get_tag(row[2], dept_id),
                    'city_id': 0,
                    'lang': 0,
                    'is_crawl': 1,
                    'short_id': '',
                    'uid': '',
                    'country': '',
                    'location': '',
                    'nickname': '',
                    'avatar': '',
                    'cover_url': '',
                    'signature': '',
                    'total_favorited': 0,
                    'following_count': 0,
                    'follower_count': 0,
                    'aweme_count': 0,
                    'favoriting_count': 0,
                    'dongtai_count': 0,
                    'gender': 0,
                    'birthday': None,
                    'sec_uid': '',
                    'province': '',
                    'city': '',
                    'dy_user_id': 0
                }

                # service = Hubservice()
                # user_data = service.create_user({'unique_id': row[0]})
                # data = data.update(dict(user_data))

                user = DyUser.where('unique_id', '=', row[0]).where('dept_id', '=', dept_id).first()
                if not user:
                    user = DyUser(data)
                    user.save()
                else:
                    user = DyUser.find(user.id)
                    for k,v in data.items():
                        setattr(user, k, v)
                    user.save()
            except Exception, e:
                print e.message

        producer = SyncMessageProducer(self.configs['amqp'])
        producer.produce({'model': 'AdminImport', 'operate': 'sync'})
        producer.close()

        return filepath

scan = ImportMessageConsumer({
    'web_path':'D:\phpstudy_pro\WWW\douyin.app\douyin-app\public',
    'amqp': settings.AMQP
})
scan.run()
