# -*- coding: utf-8 -*-
import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'

from douyin.tasks.rabbitmq import MessageProducer

class SyncMessageProducer(MessageProducer):
    """ 同步信息
    """
    # arguments = {'x-max-priority': 9}
    exchange_name = 'soren_sync_message_exchange'
    queue_name = 'soren_sync_message'
    routing_key = 'soren_sync_message'
    consumer_tag = 'soren_sync_message_consumer'