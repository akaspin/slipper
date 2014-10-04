# coding=utf-8
from __future__ import absolute_import

from kombu import Exchange, Queue
exchanges = {
    'contracts_new': Exchange(
        'slipper.contracts.new',
        durable=True,
        type='direct',
        delivery_mode='persistent'),

    # Points notifications
    'points_new': Exchange(
        'slipper.points.new',
        durable=True,
        type='direct',
        delivery_mode='persistent'),

    # Contracts reports for clients.
    'contracts_ready': Exchange(
        'slipper.contracts.ready',
        durable=True,
        type='direct',
        delivery_mode='persistent'),

    # Internal exchange
    'internal': Exchange(
        'slipper.internal',
        durable=True,
        type='direct',
        delivery_mode='persistent'),
}


queues = {
    'contracts_new': Queue(
        'slipper.contracts.new',
        exchange=exchanges['contracts_new']),
    'internal': Queue(
        'slipper.contracts.schedule',
        exchange=exchanges['internal']),
    'points_new': Queue(
        'slipper.points.new',
        exchange=exchanges['points_new'],
    )
}



