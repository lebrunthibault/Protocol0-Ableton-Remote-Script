import inspect
import sys
import types
from functools import partial

from typing import Any, Callable, Optional, Type

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


def is_lambda(func):
    # type: (Callable) -> bool
    return isinstance(func, types.LambdaType) and func.__name__ == "<lambda>"


def get_inner_func(func):
    # type: (Any) -> Callable
    if hasattr(func, "function"):
        return get_inner_func(func.function)
    if hasattr(func, "func"):  # partial
        return get_inner_func(func.func)
    if hasattr(func, "original_func"):
        return get_inner_func(func.original_func)
    if hasattr(func, "listener"):
        return get_inner_func(func.listener)

    return func


def get_class_from_func(func):
    # type: (Any) -> Optional[Type]
    if hasattr(func, "__self__"):
        return func.__self__.__class__
    elif hasattr(func, "__class__"):
        return func.__class__
    else:
        return None


def get_class_name_from_method(func):
    # type: (Any) -> str
    class_ = get_class_from_func(func)
    if class_ is None:
        raise Protocol0Error("Cannot get class_name from func")

    class_name = class_.__name__
    if class_name and all(word not in class_name for word in ["function", "None"]):
        return class_name



    try:
        if sys.version_info.major == 2:
            from qualname import qualname

            func_qualname = qualname(func)
        else:
            func_qualname = func.__qualname__

        return ".".join(func_qualname.split(".")[:-1])
    except (AttributeError, IOError):
        return "unknown %s" % func


def get_callable_repr(func):
    # type: (Any) -> str
    assert not isinstance(func, str), "func argument invalid"
    from protocol0.shared.sequence.Sequence import Sequence
    from protocol0.shared.sequence.SequenceStep import SequenceStep

    if isinstance(func, Sequence) or isinstance(func, SequenceStep):
        return func.__repr__()

    if is_lambda(func):
        return "unknown lambda"

    decorated_func = get_inner_func(func)
    class_name = get_class_name_from_method(decorated_func)
    class_name = class_name.replace(".<locals>", "")

    if not hasattr(decorated_func, "__name__"):
        func_name = str(decorated_func)
    else:
        func_name = decorated_func.__name__

    if class_name:
        return "%s.%s" % (class_name, func_name)
    else:
        return func_name


def nop(*_, **__):
    # type: (Any, Any) -> None
    pass


def is_func_equal(func1, func2, compare_methods=False):
    # type: (Callable, Callable, bool) -> bool
    """
    compare_methods == True will return True for the same method of different objects
    """
    if func1 == func2:
        return True
    elif isinstance(func1, partial) and isinstance(func2, partial):
        return func1.func == func2.func
    elif inspect.ismethod(func1) and inspect.ismethod(func2) and compare_methods:
        c1 = get_class_from_func(func1)
        c2 = get_class_from_func(func2)

        return c1 == c2 and func1.__name__ == func2.__name__
    else:
        return False
