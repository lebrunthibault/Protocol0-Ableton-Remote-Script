from typing import Optional, Any


class ForwardTo(object):
    # noinspection PyCallingNonCallable
    """
    A descriptor based recipe that makes it possible to write shorthands
    that forward attribute access from one object onto another.

    >>> class C(object):
    ...     def __init__(self):
    ...         class CC(object):
    ...             def xx(self, extra):
    ...                 return 100 + extra
    ...             foo = 42
    ...         self.cc = CC()
    ...
    ...     local_cc = ForwardTo('cc', 'xx')
    ...     local_foo = ForwardTo('cc', 'foo')
    ...
    >>> # noinspection PyCallingNonCallable
    >>> print C().local_cc(10)
    110
    >>> print C().local_foo
    42

    Arguments: objectName - name of the attribute containing the second object.
               attrName - name of the attribute in the second object.
    Returns:   An object that will forward any calls as described above.
    """

    def __init__(self, object_name, attr_name):
        # type: (str, str) -> None
        self.object_name = object_name
        self.attr_name = attr_name

    def __get__(self, instance, _=None):
        # type: (object, Optional[object]) -> None
        return getattr(getattr(instance, self.object_name), self.attr_name)

    def __set__(self, instance, value):
        # type: (object, Any) -> None
        setattr(getattr(instance, self.object_name), self.attr_name, value)

    def __delete__(self, instance):
        # type: (object) -> None
        delattr(getattr(instance, self.object_name), self.attr_name)
