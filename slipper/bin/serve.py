# coding=utf-8
from gevent import monkey
monkey.patch_all()

from logging import getLogger
import os

from gevent import get_hub, spawn
from gevent.pywsgi import WSGIServer

from slipper.env import CFG

from slipper.http.handler import app

from slipper.messaging.driver import DRIVER
from slipper.messaging.handler import ContractsNewHanler, PointsNewHandler, \
    ScheduleHandler, WaiterHandler


CFG(os.environ.get('SLIPPER_CONFIG'), {
    'http.host': os.environ.get('SLIPPER_HTTP_HOST'),
    'http.port': (os.environ.get('SLIPPER_HTTP_PORT'), int),
})


def run_forever(cb):
    hub = get_hub()
    hub.loop.run_callback(cb)
    try:
        hub.join()
    except (SystemExit, KeyboardInterrupt):
        hub.parent.throw(SystemExit())
        pass


def run_all():
    for handler in [ContractsNewHanler, PointsNewHandler,
                    ScheduleHandler, WaiterHandler]:
        spawn(DRIVER.get_consumer(handler).run)

    s = WSGIServer((CFG.http.host, CFG.http.port), app)
    spawn(s.start)
    getLogger(__name__).info('Slipper serving. HTTP on http://%s:%s',
                             CFG.http.host, CFG.http.port)


def main():
    run_forever(run_all)

if __name__ == '__main__':
    main()
