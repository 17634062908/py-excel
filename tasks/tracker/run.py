# -*- coding: utf-8 -*-
import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'

import os
import sys
import logging

from douyin.core import settings

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
                    format='%(asctime)s %(name)s[%(process)d] %(levelname)s> %(message)s')

def _abort(err=None, prefix=None):
    if err is None:
        err = sys.exc_info()[1]
    if isinstance(err, str):
        msg = err
    else:
        msg = err[0]
    if prefix is not None:
        msg = '%s: %s' % (prefix, msg)

    sys.exit('\n' + msg + '\n')


def _load(filename, g, l):
    if not os.path.exists(filename):
        raise RuntimeError, "Configuration file %s is not exists" % filename
    if not os.path.isfile(filename):
        raise RuntimeError, "Configuration file %s is not a file" % filename

    try:
        fileObj = open(filename, 'r')
    except:
        raise RuntimeError, "Error reading configuration file %s" % filename

    def include(filepath):
        if not os.path.isabs(filepath):
            filepath = os.path.join(os.path.dirname(filename), filepath)
        execfile(filepath, g, l)

    g = { 'include': include }

    try:
        exec fileObj in g, l
    except:
        print sys.exc_info()[1]
        raise RuntimeError("Error parsing configuration file %s, "
                    "make sure the syntex is right.(it should be a valid" 
                    "python source file)." % filename)


def load_config(filename):
    d = {'__file__': os.path.abspath(filename),
        'DOUYIN_TASK_HOME': os.environ['DOUYIN_TASK_HOME'] }

    try:
        _load(filename, d, d)
    except:
        _abort()

    settings.__dict__.update(d)


def run():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-c", "--conf", dest="conf",
                      default=os.path.join(os.environ['DOUYIN_TASK_HOME'], 'conf', 'tasks.conf'),
                      help="configuration file")
    parser.add_option("-d", "--deamon",
                      action="store_true", dest="daemonize", default=False,
                      help="run as a deamon process")
    parser.add_option("-r", "--run", dest="run",
                      help="just run one kind of app: collector or fetcher")
    options, args = parser.parse_args()

    load_config(options.conf)

    if options.run is not None:
        settings.__dict__['PROCESSES'] = [options.run]

    if options.daemonize:
        from douyin.tasks.tracker.daemon import daemonize
        daemonize(stderr = settings.LOG_PATH)

    from douyin.tasks.tracker import Tracker
    Tracker().run()