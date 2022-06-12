import inspect
import types

from qualname import qualname
from typing import Any, Callable

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


def is_method(func):
    # type: (Callable) -> bool
    spec = inspect.getargspec(func)
    return bool(spec.args and (spec.args[0] == "self" or spec.args[0] == "cls"))


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


def get_class_name_from_method(func):
    # type: (Any) -> str
    if hasattr(func, "__self__"):
        class_name = func.__self__.__class__.__name__
    elif hasattr(func, "__class__"):
        class_name = func.__class__.__name__
    else:
        raise Protocol0Error("Cannot get class_name from func")

    if class_name and all(word not in class_name for word in ["function", "None"]):
        return class_name

    try:
        return ".".join(qualname(func).split(".")[:-1])
    except (AttributeError, IOError):
        return "unknown %s" % func


def get_callable_repr(func):
    # type: (Any) -> str
    from protocol0.shared.sequence.Sequence import Sequence
    from protocol0.shared.sequence.SequenceStep import SequenceStep
    if isinstance(func, Sequence) or isinstance(func, SequenceStep):
        return func.__repr__()

    decorated_func = get_inner_func(func)
    class_name = get_class_name_from_method(decorated_func)

    if not hasattr(decorated_func, "__name__"):
        return "only class_name %s" % class_name or "unknown"

    if class_name:
        return "%s.%s" % (class_name, decorated_func.__name__)
    else:
        return decorated_func.__name__


def nop(*_, **__):
    # type: (Any, Any) -> None
    pass
