# coding=utf-8

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from slipper.utils.decorators import cached_property


class Boot(object):

    def __init__(self, url=None):
        self.url = url

    @cached_property
    def engine(self):
        return create_engine(self.url)

    @cached_property
    def Session(self):
        return sessionmaker(bind=self.engine)
