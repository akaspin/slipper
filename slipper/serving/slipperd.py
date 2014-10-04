# coding=utf-8
from gevent import monkey
monkey.patch_all()

from gevent import get_hub, spawn

from slipper.env import getLogger

from slipper.messaging.handler import ContractsNewHanler, PointsNewHandler, \
    InternalHandler
from slipper.messaging.interface import interface


LOG = getLogger(__name__)


def run_forever(cb):
    hub = get_hub()
    hub.loop.run_callback(cb)
    try:
        hub.join()
    except (SystemExit, KeyboardInterrupt):
        pass


def run_all():
    for handler in [ContractsNewHanler, PointsNewHandler, InternalHandler]:
        spawn(interface.adapter.get_consumer(handler).run)


def main():
    run_forever(run_all)

main()
