import inspect
import types
from collections import namedtuple
from types import FrameType

from qualname import qualname
from typing import Optional, Any, List, cast, Callable, TYPE_CHECKING

from a_protocol_0.consts import ROOT_DIR, REMOTE_SCRIPTS_DIR
from a_protocol_0.my_types import StringOrNumber, T

if TYPE_CHECKING:
    from a_protocol_0.lom.AbstractObject import AbstractObject


def scroll_object_property(base_object, property, items, go_next):
    # type: (T, str, List[T], bool) -> None
    new_value = scroll_values(items, getattr(base_object, property), go_next)
    setattr(base_object, property, new_value)
    from a_protocol_0 import Protocol0

    Protocol0.SELF.show_message("Selected %s" % new_value)


def scroll_values(items, selected_item, go_next):
    # type: (List[T], T, bool) -> T
    if len(items) == 0:
        return selected_item
    increment = 1 if go_next else -1
    index = 0
    try:
        index = (items.index(selected_item) + increment) % len(items)
        return items[index]
    except ValueError:
        return selected_item


def find_if(predicate, seq):
    # type: (Callable[[T], bool], List[T]) -> Optional[T]
    for x in seq:
        if predicate(x):
            return x
    return None


def find_where(predicate, seq):
    # type: (Callable[[T], bool], List[T]) -> List[T]
    return [x for x in seq if predicate(x)]


def find_last(predicate, seq):
    # type: (Callable[[T], bool], List[T]) -> Optional[T]
    items = find_where(predicate, seq)
    return items[-1] if len(items) else None


def is_equal(val1, val2, delta=0.00001):
    # type: (StringOrNumber, StringOrNumber, float) -> bool
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        return abs(val1 - val2) < delta
    else:
        return val1 == val2


def have_equal_properties(obj1, obj2, properties):
    # type: (AbstractObject, AbstractObject, List[str]) -> bool
    for property in properties:
        if (
            not hasattr(obj1, property)
            or not hasattr(obj2, property)
            or not is_equal(getattr(obj1, property), getattr(obj2, property))
        ):
            return False
    return True


def clamp(val, minv, maxv):
    # type: (int, int, int) -> int
    return max(minv, min(val, maxv))


def get_frame_info(frame_count=1):
    # type: (int) -> Optional[Any]
    try:
        call_frame = inspect.currentframe()
        for _ in range(frame_count):
            call_frame = call_frame.f_back
        (filename, line, method_name, _, _) = inspect.getframeinfo(cast(FrameType, call_frame))
    except Exception:
        return None

    filename = filename.replace(ROOT_DIR + "\\", "").replace(REMOTE_SCRIPTS_DIR + "\\", "")
    class_name = filename.replace(".py", "").split("\\")[-1]

    FrameInfo = namedtuple("FrameInfo", ["filename", "class_name", "line", "method_name"])
    return FrameInfo(filename=filename, class_name=class_name, line=line, method_name=method_name)


def _has_callback_queue(func):
    # type: (Any) -> bool
    """ mixing duck typing and isinstance to ensure we really have a callback handler object """
    from a_protocol_0.utils.callback_descriptor import CallableWithCallbacks
    from _Framework.SubjectSlot import CallableSlotMixin

    return (
        func
        and hasattr(func, "add_callback")
        and (isinstance(func, CallableWithCallbacks) or isinstance(func, CallableSlotMixin))
    )


def is_method(func):
    # type: (Callable) -> bool
    spec = inspect.getargspec(func)
    return bool(spec.args and spec.args[0] == "self")


def is_partial(func):
    # type: (Callable) -> bool
    return "functools.partial" in str(type(func))


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

    if class_name and all(word not in class_name for word in ["function", "None"]):
        return class_name

    try:
        return ".".join(qualname(func).split(".")[:-1])
    except AttributeError:
        pass

    return ""


def get_callable_name(func, obj=None):
    # type: (Callable, object) -> str
    from a_protocol_0.sequence.Sequence import Sequence

    if isinstance(func, Sequence):
        return func.name

    decorated_func = get_inner_func(func)
    if obj:
        class_name = str(obj) if hasattr(obj, "__repr__") else obj.__class__.__name__
    else:
        class_name = get_class_name_from_method(decorated_func)

    if not hasattr(decorated_func, "__name__"):
        return class_name or "unknown"

    if class_name:
        return "%s.%s" % (class_name, decorated_func.__name__)
    else:
        return decorated_func.__name__


def _arg_count(func):
    # type: (Any) -> int
    """Note : this is not ideal because we cannot know if the defaults are already set by e.g a partial function
    Thus we could be subtracting twice a parameter,
    but that's better than to have an outer function setting a mismatched parameter
    """
    if is_partial(func):
        spec = inspect.getargspec(func.func)
        arg_len = len(spec.args) - len(func.args) - len(func.keywords)
        if "self" in spec.args:
            arg_len -= 1
    else:
        spec = inspect.getargspec(func)
        arg_len = len(spec.args)
    arg_len -= len(spec.defaults) if spec.defaults else 0
    arg_count = arg_len if (isinstance(func, types.FunctionType) or is_partial(func)) else arg_len - 1
    return max(arg_count, 0)


def nop():
    # type: () -> None
    pass


def flatten(t):
    # type: (List[List[T]]) -> List[T]
    return [item for sublist in t for item in sublist]


def scale_from_value(value, min_a, max_a, min_b, max_b):
    # type: (float, float, float, float, float) -> float
    return float(float((max_b - min_b) * (value - min_a)) / (max_a - min_a)) + min_b
