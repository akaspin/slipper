from __future__ import absolute_import

import sys


def detect_environment():

    # -gevent-
    if 'gevent' in sys.modules:
        try:
            from gevent import socket as _gsocket
            import socket

            if socket.socket is _gsocket.socket:
                return 'gevent'
        except ImportError:
            pass

    return 'sync'
