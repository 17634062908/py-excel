# -*- coding: utf-8 -*-
import logging

import pika
import sys

from douyin.core import settings

try:
    # For Python < 2.6 or people using a newer version of simplejson
    import simplejson as json
except ImportError:
    # For Python >= 2.6
    import json

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
                    format='%(asctime)s %(name)s[%(process)d] %(levelname)s> %(message)s')
LOG = logging.getLogger('MsgConsumer')


class MessageConsumer(object):  # {{{
    conn = None
    chan = None
    exchange_name = None
    queue_name = None
    routing_key = None
    consumer_tag = None
    exchange_type = 'direct'
    no_ack = False
    arguments = {'x-max-priority': 9}

    # arguments = {}

    def consume(self, cfg):
        credentials = pika.PlainCredentials(username=cfg['user'], password=cfg['passwd'])
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=cfg['host'], port=cfg['port'], virtual_host=cfg['vhost'],
                                      credentials=credentials, heartbeat=0))
        self.chan = self.conn.channel()

        # self.chan.access_request(cfg['vhost'], active=True, read=True)
        self.chan.queue_declare(queue=self.queue_name, durable=True, exclusive=False, auto_delete=False,
                                arguments=self.arguments)
        self.chan.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type, durable=True,
                                   auto_delete=False)
        self.chan.queue_bind(queue=self.queue_name, exchange=self.exchange_name, routing_key=self.routing_key)

        self.chan.basic_qos(prefetch_count=2)
        self.chan.basic_consume(queue=self.queue_name, auto_ack=self.no_ack, on_message_callback=self.handle_raw_msg,
                                consumer_tag=self.consumer_tag)

        # while self.chan.on_message_callback:
        #    self.chan.wait()
        # self.chan.basic_cancel(self.consumer_tag)
        try:
            self.chan.start_consuming()
        except Exception, e:  # when connection is lost, e.g. rabbitmq not running
            logging.error("Lost connection %s" % str(e))

        # self.chan.close()
        # self.conn.close()


    def handle_raw_msg(self, ch, method, properties, raw_msg):
        try:
            msg = json.loads(raw_msg)
            self.handle_msg(msg)
        except Exception, e:
            print(str(e))

    def handle_msg(self, msg):
        pass


class MessageProducer(object):
    exchange_name = None
    queue_name = None
    routing_key = None
    consumer_tag = None
    arguments = {'x-max-priority': 9}
    # arguments = {}
    exchange_type = 'direct'  # fanout

    def __init__(self, cfg):
        credentials = pika.PlainCredentials(username=cfg['user'], password=cfg['passwd'])
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(host=cfg['host'], port=cfg['port'], virtual_host=cfg['vhost'],
                                      credentials=credentials, heartbeat=0))
        self.chan = self.conn.channel()
        # self.chan.access_request(cfg['vhost'], active=True, read=True)
        self.chan.queue_declare(queue=self.queue_name, durable=True, exclusive=False, auto_delete=False,
                                arguments=self.arguments)
        self.chan.exchange_declare(exchange=self.exchange_name, exchange_type=self.exchange_type, durable=True,
                                   auto_delete=False)
        self.chan.queue_bind(queue=self.queue_name, exchange=self.exchange_name, routing_key=self.routing_key)

    def produce(self, msg, props={}):
        msg = json.dumps(msg)
        properties = pika.BasicProperties(**props)
        # print msg, properties.priority
        # msg = amqp.Message(msg)
        # for k, v in props.iteritems():
        #    msg.properties[k] = v
        self.chan.basic_publish(self.exchange_name, self.routing_key, msg, properties=properties)

    def close(self):
        self.chan.close()
        self.conn.close()

    def delete(self):
        self.chan.queue_delete(self.queue_name)