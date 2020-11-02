# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'

import requests
import json
import logging
from redis import StrictRedis
from douyin.core.settings import REDIS
from douyin.core import settings

redis = StrictRedis(host=REDIS.get('host'), port=REDIS.get('port'), db=REDIS.get('db'))

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
                    format='%(asctime)s %(name)s[%(process)d] %(levelname)s> %(message)s')
LOG = logging.getLogger('hubservice')

class Hubservice:

    def __init__(self):
        self._base_url = settings.HUB.get('client_api_url')
        self._token_url = settings.HUB.get('client_token_url')
        self._key = settings.HUB.get('client_id')
        self._secret = settings.HUB.get('client_secret')

    def request(self, url, data):
        url = url if self._base_url.endswith('/') else  self._base_url + '/' + url
        access_token = self.access_token()

        if not access_token:
            access_token = self.access_token(False)
            if not access_token:
                raise Exception('登录中心服务器失败')

        try:
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + access_token
            }
            response = requests.post(url, data, headers=headers)
            result = json.loads(response.text)

            if response.status_code != 200:
                error_msg = result.get('message')
                raise Exception(error_msg)

            return result.get('data')
        except Exception, e:
            LOG.error(e)

    def access_token(self, is_cache=True):
        cache_key = 'access_token@douyin_hub'
        access_token = redis.get(cache_key)
        if not access_token or not is_cache:
            try:
                data = {
                    'grant_type': 'client_credentials',
                    'client_id': self._key,
                    'client_secret': self._secret,
                    'scope': '*'
                }
                response = requests.post(self._token_url, data)
                result = json.loads(response.text)
                redis.set(cache_key, result.get('access_token'))

                return access_token
            except Exception, e:
                LOG.error(e)

    def create_user(self, data):
        url = 'dy_user/create'
        return self.request(url, data)

c =  Hubservice()
c.create_user({'unique_id': 10})
