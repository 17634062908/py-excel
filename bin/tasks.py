# -*- coding: utf-8 -*-
import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'

import sys, os, string

script = os.path.abspath(sys.argv[0])

if string.find(script, os.sep + 'douyin') != -1:
    home = os.path.normpath(os.path.join(os.path.dirname(script), os.pardir))
    sys.path.insert(0, home)
    print 'home path: %s ' % home
    os.environ['DOUYIN_TASK_HOME'] = home
if hasattr(os, "getuid") and os.getuid() != 0:
    sys.path.insert(0, os.path.abspath(os.getcwd()))

del script
### end of preamble

# start application
from douyin.tasks.tracker.run import run

run()
