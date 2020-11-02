# -*- coding: utf-8 -*-
import sys
import json

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'

str = "{'name': 'hello, 'age': 22}"
print json.loads(str)


