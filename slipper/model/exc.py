# coding=utf-8

from slipper.exc import SlipperException


class SlipperModelException(SlipperException):
    pass


class InvalidContractDataError(SlipperModelException):
    message = 'Invalid contract data: %(data)s.'


class NotRoutedContractError(SlipperModelException):
    message = 'Contract has no route: %(data)s.'


class InvalidPointData(SlipperModelException):
    message = 'Invalid point data: %(data)s'
