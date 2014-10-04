"""Contains some useful decorators."""
from __future__ import absolute_import

from abc import ABCMeta, abstractmethod
from functools import update_wrapper
from threading import RLock


def create_lock(name, cls=RLock):
    """Create lock bounded to object."""
    global_lock = cls()
    name = '_{0}_lock'.format(name)

    def inner(obj):
        try:
            return obj.__dict__[name]
        except KeyError:
            with global_lock:
                try:
                    return obj.__dict__[name]
                except KeyError:
                    lock = obj.__dict__[name] = cls()
                    return lock

    return inner


class Store(object):
    """Store implementation."""

    __metaclass__ = ABCMeta

    def __init__(self, factory):
        self.__instances = {}
        self.__factory = factory

    def __getitem__(self, key):
        """Create new item."""
        try:
            instance = self.__instances[key]
        except KeyError:
            instance = self.__instances[key] = self.__factory(key)
        return instance

    def __delitem__(self, key):
        """Delete instance by it's key."""
        self.__instances.pop(key, None)

    def __getattr__(self, key):
        """Get instance by it's key."""
        return self[key]

    def __call__(self, key):
        """Return item by key."""
        return self[key]

    def clear(self):
        """Clear all created instances."""
        self.__instances.clear()
    reset = clear


class Factory(Store):
    """Basic factory implementation. Acts as subscriptable. Provides lazy
    instance initialization.

    You can access elements by it's key::

        class SomeFactory(Factory):
            def create(key):
                return SomeClass(key)

        factory = SomeFactory()
        instance = factory['some_key']

    """

    def __init__(self):
        super(Factory, self).__init__(self.create)

    @abstractmethod
    def create(self, key):
        """Create new instance."""
        raise NotImplementedError('Subclass responsibility')

    @abstractmethod
    def keys(self):
        """Return all supported keys."""
        raise NotImplementedError('Subclass responsibility')

    def __dir__(self):
        attrs = set(dir(type(self)) + list(vars(self)))
        attrs.update(self.keys())
        return list(attrs)

    def __contains__(self, key):
        """Check that given key exists."""
        return key in self.keys()

    def items(self):
        """Return key to entity mapping."""
        return {k: self[k] for k in self.keys()}


class cached_property(object):
    """Property descriptor that caches the return value
    of the get function.

    *Examples*

    .. code-block:: python

        @cached_property
        def connection(self):
            return Connection()

        @connection.setter  # Prepares stored value
        def connection(self, value):
            if value is None:
                raise TypeError('Connection must be a connection')
            return value

        @connection.deleter
        def connection(self, value):
            # Additional action to do at del(self.attr)
            if value is not None:
                print('Connection %r deleted' % (value, ))

    """

    def __init__(self, fget, fset=None, fdel=None, doc=None):
        self.__get = fget
        self.__set = fset
        self.__del = fdel
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        try:
            return obj.__dict__[self.__name__]
        except KeyError:
            value = obj.__dict__[self.__name__] = self.__get(obj)
            return value

    def __set__(self, obj, value):
        if obj is None:
            return self
        if self.__set is not None:
            value = self.__set(obj, value)
        obj.__dict__[self.__name__] = value

    def __delete__(self, obj):
        if obj is None:
            return self
        try:
            value = obj.__dict__.pop(self.__name__)
        except KeyError:
            pass
        else:
            if self.__del is not None:
                self.__del(obj, value)

    def setter(self, fset):
        return self.__class__(self.__get, fset, self.__del)

    def deleter(self, fdel):
        return self.__class__(self.__get, self.__set, fdel)


class cached_factory(cached_property):
    """Simple cached factory."""

    Store = Store

    def __init__(self, fget, doc=None):
        factory = lambda obj: self.Store(fget.__get__(obj))
        factory = update_wrapper(factory, fget)
        super(cached_factory, self).__init__(factory, doc=doc)

    def setter(self, fset):
        raise NotImplementedError()

    def deleter(self, fdel):
        raise NotImplementedError()

# for compatibility
synchronized_factory = cached_factory


class synchronized_property(cached_property):
    """Cached property with thread-safe initialization."""

    def __init__(self, fget, fset=None, fdel=None, doc=None):
        super(synchronized_property, self).__init__(fget, fset, fdel, doc)
        self.__lock = create_lock(self.__name__)

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        try:
            return obj.__dict__[self.__name__]
        except KeyError:
            with self.__lock(obj):
                return super(synchronized_property, self).__get__(obj, type)

    def __set__(self, obj, value):
        with self.__lock(obj):
            super(synchronized_property, self).__set__(obj, value)

    def __delete__(self, obj):
        with self.__lock(obj):
            super(synchronized_property, self).__delete__(obj)
