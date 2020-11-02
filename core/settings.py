# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'

LOG_LEVEL = 'WARN'

DATABASES = {
    'default': 'cluster',
    'cluster': {
        'driver': 'mysql',
        'host': 'localhost',
        'database': 'douyin',
        'user': 'root',
        'password': 'root',
        'charset': 'utf8mb4',
    },
    'cluster_id': {
        'driver': 'mysql',
        'host': '127.0.0.1',
        'database': 'soren_cluster_id',
        'user': 'root',
        'password': '123123',
        'charset': 'utf8mb4',
    }
}

SERVICES = {
    'hub': {

    }
}

AMQP = {
    'host': '127.0.0.1',
    'port': 5672,
    'user': 'guest',
    'passwd': 'guest',
    'vhost': '/'
}

REDIS = {
    'host': '127.0.0.1',
    'port': 6379,
    'db': 0
}

HUB = {
    'client_id': 8,
    'client_secret': 'WkT9rqTV40zWj9bHp7geqlpXvSWWmds6jowGwcb9',
    'client_callback': 'http://douyin.test/console/auth/censor/callback',
    'client_token_url': 'http://censor.test/oauth/token',
    'client_api_url': 'http://censor.test/api/v1'
}
