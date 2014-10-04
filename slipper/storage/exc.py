# coding=utf-8

from slipper.exc import SlipperException


class StorageException(SlipperException):
    message = 'Unknown storage error %s.'


class NotFoundError(StorageException):
    """Raises when model entity not found"""
    message = "%(entity)s %(uid)s not found."


class NotUniqueError(StorageException):
    """Raises when model entity not found"""
    message = "%(entity)s %(uid)s already exists."

