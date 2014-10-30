# coding=utf-8
"""
AMQP mappings.

Source - queue, Target - exchange.

Contracts.
Exchange: 'slipper.contracts'
Queue: 'slipper.contracts.new' (routing: None)
Queue: 'slipper.contracts.schedule' (routing: 'schedule')

Points.
Exchange: 'slipper.points'
Queue: 'slipper.points.new' (routing: None)
Queue: 'slipper.points.<route>' (routing: <route>)
"""
from kombu import Exchange, Queue

from slipper.env import CFG
from slipper.utils.proxy import PromiseProxy


_exchanges = {
    'contracts': Exchange(
        'slipper.contracts',
        durable=True,
        type='direct',
        delivery_mode='persistent'),
    'points': Exchange(
        'slipper.points',
        durable=True,
        type='direct',
        delivery_mode='persistent'),
}

SOURCES = {
    ('contracts', 'new'): Queue(
        'slipper.contracts.new',
        exchange=_exchanges['contracts'],
        routing_key='new'),
    ('contracts', 'schedule'): Queue(
        'slipper.contracts.schedule',
        exchange=_exchanges['contracts'],
        routing_key='schedule'),
    ('points', 'new'): Queue(
        'slipper.points.new',
        exchange=_exchanges['points'],
        routing_key='new'),
    ('points', None): Queue(
        'slipper.points.%s' % CFG.process_uuid,
        auto_delete=True,
        exchange=_exchanges['points'],
        routing_key=CFG.process_uuid),
}

DESTINATIONS = {
    ('contracts', 'new'): None
}
