# coding=utf-8

from importlib import import_module


def class_for_name(name):
    """Get class for full name.

    :param str name: Full class name.
    :rtype: function
    """
    module_name, class_name = name.rsplit('.', 1)
    mod = import_module(module_name)
    return getattr(mod, class_name)
