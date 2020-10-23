# -*- coding: utf-8 -*-
import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'

import logging
try:
    # For Python < 2.6 or people using a newer version of simplejson
    import simplejson as json
except ImportError:
    # For Python >= 2.6
    import json
from douyin.core import settings
from douyin.tasks.rabbitmq import MessageConsumer

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
                    format='%(asctime)s %(name)s[%(process)d] %(levelname)s> %(message)s')
LOG = logging.getLogger('Consumers')

class AckMessageConsumer(MessageConsumer):
    no_ack = False

    def __init__(self, configs=None):
        self.configs = configs

    def run(self):
        try:
            self.consume(self.configs['amqp'])
        except Exception, e:
            LOG.error("Unknown run[%s]" % str(e), exc_info=True)

    def handle_raw_msg(self, ch, method, properties, raw_msg):
        try:
            self.properties = properties
            self.raw = raw_msg
            msg = json.loads(raw_msg)
            self.handle_msg(msg)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception, e:
            LOG.error("Consumer[%s][%s]" % (str(e), raw_msg))