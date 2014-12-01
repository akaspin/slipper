# coding=utf-8
from gevent import monkey
monkey.patch_all()

from logging import getLogger
import os

from gevent import get_hub, spawn

from slipper.env import CFG


from slipper.messaging.driver import DRIVER
from slipper.messaging.handler import ContractsNewHanler, PointsNewHandler, \
    SchedulerHandler


CFG(os.environ.get('SLIPPER_CONFIG'))


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
                    SchedulerHandler]:
        spawn(DRIVER.get_consumer(handler).run)

    # s = WSGIServer((CFG.http.host, CFG.http.port), app)
    # spawn(s.start)
    # getLogger(__name__).info('Slipper serving. HTTP on http://%s:%s',
    #                          CFG.http.host, CFG.http.port)


def main():
    run_forever(run_all)

if __name__ == '__main__':
    main()
