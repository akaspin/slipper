# coding=utf-8

import functools

from six import reraise

from slipper.env import getLogger
from slipper.storage.interface import interface


#: Logging
LOG = getLogger(__name__)


class Transaction(object):
    """Session context"""

    def __init__(self, session=None, autoflush=False, autocommit=False,
                 commit_on=None, no_raise=None):
        """
        :param session: Session.
        :param bool autoflush: Session auto flush.
        :param bool autocommit: Auto commit.
        :param commit_on: Commit regardless these exceptions.
        :param no_raise: Don't raise this error after rollback.
        :type commit_on: list
        :type session: :py:class:`sqlalchemy.orm.session.Session`
        """
        #: Top level.
        self.commit_on = commit_on or []
        self.no_raise = no_raise or []
        self.autoflush = autoflush
        self.autocommit = autocommit
        self.session = session
        super(Transaction, self).__init__()

    def __enter__(self):
        if self.session is None:
            self.session = interface.boot.Session(
                autoflush=self.autoflush,
                autocommit=self.autocommit)
        else:
            self.session.begin_nested()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return self.__commit()
        for nr in self.commit_on:
            if exc_type is nr or issubclass(exc_type, nr):
                LOG.debug('%s, Recoverable: %s, %s',
                            self.__by_level(), exc_type, exc_val)
                return self.__commit()
        LOG.warning('%s FAIL: %s, %s', self.__by_level(), exc_type, exc_val)
        self.session.rollback()
        if self.__check_error(exc_type, self.no_raise):
            return True
        reraise(exc_type, exc_val, exc_tb)

    @staticmethod
    def __check_error(exc_type, blessed_errors):
        return exc_type in blessed_errors or any(
            issubclass(exc_type, be) for be in blessed_errors)

    def __commit(self):
        self.session.commit()
        return True

    def __by_level(self):
        n = self.session.transaction.nested.numerator
        return ('Transaction'
                if n == 0 else
                'Transaction (level %s)' % n)


def with_transaction(commit_on=None, no_raise=None):
    def param_wrapper(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with Transaction(session=kwargs.get('session'),
                             commit_on=commit_on,
                             no_raise=no_raise) as session_ctx:
                kwargs.update({'session': session_ctx})
                return fn(*args, **kwargs)
        return wrapper
    return param_wrapper
