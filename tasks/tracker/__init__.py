# -*- coding: utf-8 -*-
import sys

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    print 'set default encoding error'


import sys
import os
import socket
import select
import errno
import signal
import logging
import time

try:
    import fcntl
except ImportError:
    def setCloseOnExec(sock):
        pass
else:
    def setCloseOnExec(sock):
        fcntl.fcntl(sock.fileno(), fcntl.F_SETFD, fcntl.FD_CLOEXEC)

from douyin.core import settings

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
                    format='%(asctime)s %(name)s[%(process)d][%(module)s-%(lineno)d] %(levelname)s> %(message)s')
LOG = logging.getLogger('Tracker')

try:
    from setproctitle import setproctitle
    setproctitle('SOREN_TASK')
except:
    pass

class Tracker(object):
    def __init__(self):
        self._children = {}

    def run(self):
        # Set up signal handlers.
        self._keepGoing = True
        self._hupReceived = False
        self._installSignalHandlers()

        # Main loop.
        while self._keepGoing:
            for proc in settings.PROCESSES:
                self._spawnChildren(getattr(settings, '%s_SETTINGS' % proc.upper()))

            # Wait on any socket activity from live children.
            r = [x['file'] for x in self._children.values() if x['file'] is not None]

            if len(r) == len(self._children):
                timeout = None
            else:
                # There are dead children that need to be reaped, ensure
                # that they are by timing out, if necessary.
                timeout = 2

            try:
                r, w, e = select.select(r, [], [], timeout)
            except select.error, e:
                if e[0] != errno.EINTR:
                    raise

            # Scan child sockets and tend to those that need attention.
            for child in r:
                # Receive status byte.
                try:
                    state = child.recv(1)
                except socket.error, e:
                    if e[0] in (errno.EAGAIN, errno.EINTR):
                        # Guess it really didn't need attention?
                        continue
                    raise
                # Try to match it with a child. (Do we need a reverse map?)
                for pid, d in self._children.items():
                    if child is d['file']:
                        if state: state = ord(state)
                        LOG.debug('Msg from %s[%s]: %s', d['type'], pid, state)
                        if state:
                            # Set availability status accordingly.
                            self._children[pid]['alive'] = state != '\x00'
                        else:
                            # Didn't receive anything. Child is most likely
                            # dead.
                            LOG.debug('%s[%s] is likely dead', d['type'], pid)
                            d = self._children[pid]
                            d['file'].close()
                            d['file'] = None

            # Reap children.
            self._reapChildren()
        # end while

        # Clean up all child processes.
        self._cleanupChildren()

        # Restore signal handlers.
        self._restoreSignalHandlers()

        # Return bool based on whether or not SIGHUP was received.
        return self._hupReceived


    def _spawnChildren(self, worker_settings):
        alive = 0
        for x in self._children.values():
            if x['type'] == worker_settings['name']:
                alive += 1
        workers = worker_settings['workers']
        while alive < workers:
            if not self._spawnChild(worker_settings): break
            alive += 1


    def _cleanupChildren(self):
        """
        Closes all child sockets (letting those that are available know
        that it's time to exit). Sends SIGINT to those that are currently
        processing (and hopes that it finishses ASAP).

        Any children remaining after 10 seconds is SIGKILLed.
        """
        # Let all children know it's time to go.
        for pid, d in self._children.items():
            if d['file'] is not None:
                d['file'].close()
                d['file'] = None

        def alrmHandler(signum, frame):
            pass

        # Set up alarm to wake us up after 10 seconds.
        oldSIGALRM = signal.getsignal(signal.SIGALRM)
        signal.signal(signal.SIGALRM, alrmHandler)
        signal.alarm(10)

        # Wait for all children to die.
        while len(self._children):
            try:
                pid, status = os.wait()
            except OSError, e:
                if e[0] in (errno.ECHILD, errno.EINTR):
                    break
            if self._children.has_key(pid):
                del self._children[pid]

        signal.signal(signal.SIGALRM, oldSIGALRM)

        # Forcefully kill any remaining children.
        for pid in self._children.keys():
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError, e:
                if e[0] != errno.ESRCH:
                    raise

    def _reapChildren(self):
        """Cleans up self._children whenever children die."""
        while True:
            try:
                pid, status = os.waitpid(-1, os.WNOHANG)
            except OSError, e:
                if e[0] == errno.ECHILD:
                    break
                raise
            if pid <= 0:
                break
            if self._children.has_key(pid): # Sanity check.
                if self._children[pid]['file'] is not None:
                    self._children[pid]['file'].close()
                del self._children[pid]

    def _spawnChild(self, worker_settings):
        """
        Spawn a single child. Returns True if successful, False otherwise.
        """
        # This socket pair is used for very simple communication between
        # the parent and its children.
        LOG.info('spawnChild %s ...', worker_settings['name'])
        parent, child = socket.socketpair()
        parent.setblocking(0)
        setCloseOnExec(parent)
        child.setblocking(0)
        setCloseOnExec(child)
        try:
            pid = os.fork()
        except OSError, e:
            if e[0] in (errno.EAGAIN, errno.ENOMEM):
                return False # Can't fork anymore.
            raise
        if not pid:
            # Child
            child.close()
            # Put child into its own process group.
            pid = os.getpid()
            os.setpgid(pid, pid)
            # Restore signal handlers.
            self._restoreSignalHandlers()
            # Close copies of child sockets.
            for f in [x['file'] for x in self._children.values() if x['file'] is not None]:
                f.close()
            self._children = {}
            try:
                # Enter main loop.
                self._child(worker_settings, parent)
            except:
                pass
            sys.exit(0)
        else:
            # Parent
            parent.close()
            d = self._children[pid] = {}
            d['file'] = child
            d['avail'] = True
            d['type'] = worker_settings['name']
            return True

    def _child(self, worker_settings, parent):
        """Main loop for children."""
        worker_name = worker_settings['name']
        try:
            from setproctitle import setproctitle
            setproctitle('SOREN_TASK-[worker: %s]' % worker_name)
        except:
            pass
        mod_name = worker_settings['class']
        mod_name, clas_name = mod_name.rsplit('.', 1)
        try:
            mod = __import__(mod_name)
            components = mod_name.split('.')
            for comp in components[1:]:
                mod = getattr(mod, comp)
            clas = getattr(mod, clas_name)
            print worker_settings
            sys.exit(1)
            worker = clas(worker_settings)
        except Exception, e:
            LOG.error(str(e), exc_info=True)
            raise RuntimeError, e[0]

        while True:
            # Wait for any activity on the main socket or parent socket.
            r, w, e = select.select([parent], [], [], 10)

            for f in r:
                # If there's any activity on the parent socket, it
                # means the parent wants us to die or has died itself.
                # Either way, exit.
                if f is parent:
                    return

            # Do the job.
            try:
                worker.run()
            except:
                LOG.error("Exception occurred in worker[%s]" % worker_settings['name'], exc_info=True)

            if worker_settings['interval']:
                try:
                    time.sleep(worker_settings['interval'])
                except:
                    pass

            # Tell parent we're alive.
            try:
                parent.send('\xff')
            except socket.error, e:
                if e[0] == errno.EPIPE:
                    # Parent is gone.
                    return
                raise

    # Signal handlers

    def _hupHandler(self, signum, frame):
        self._keepGoing = False
        self._hupReceived = True

    def _intHandler(self, signum, frame):
        LOG.info('Turn off...')
        self._keepGoing = False

    def _chldHandler(self, signum, frame):
        # Do nothing (breaks us out of select and allows us to reap children).
        pass

    def _installSignalHandlers(self):
        supportedSignals = [signal.SIGINT, signal.SIGTERM]
        if hasattr(signal, 'SIGHUP'):
            supportedSignals.append(signal.SIGHUP)

        self._oldSIGs = [(x,signal.getsignal(x)) for x in supportedSignals]

        for sig in supportedSignals:
            if hasattr(signal, 'SIGHUP') and sig == signal.SIGHUP:
                signal.signal(sig, self._hupHandler)
            else:
                signal.signal(sig, self._intHandler)

    def _restoreSignalHandlers(self):
        """Restores previous signal handlers."""
        for signum, handler in self._oldSIGs:
            signal.signal(signum, handler)