"""
    Base utilities related to metaclasses
    =====================================
    This module provides utilities allowing to manage metaclasses in the context of LXDock.
    LXDock uses metaclasses to implement plugin-like components like guests, hosts, ...
"""


def with_metaclass(meta, *bases):
    """ Creates a base class with a metaclass.

    This function defines a `metaclass` class that inherits from the passed `meta` metaclass and
    returns a new class whose properties will differ depending on the class being constructed:

    * if we are considering the base class to which the `with_metaclass` function was applied, a new
      class without base classes will be constructed

    * if we are considering a subclass of the class to which the `with_metaclass` function was
      applied, the class being constructed will inherit from the `meta` metaclass

    This trick is usefull to differentiate the class to which the `with_metaclass` function was
    applied from its subclasses during the execution of the `__new__` magic method (which is defined
    inside the `meta` metaclass). This allows fine control over instances created with the `meta`
    metaclass.
    """
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('NewBase', None, {})
