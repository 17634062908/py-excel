# -*- coding: utf-8 -*-
import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'

import requests

class Hubservice:

    def __init__(self, configs):
        self.configs = configs

    def get_access_token(self):
        url = self.configs.get('url')

