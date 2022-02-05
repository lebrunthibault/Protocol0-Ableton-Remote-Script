import inspect
import types
from collections import namedtuple, Sequence as CollectionsSequence
from types import FrameType

from qualname import qualname
from typing import Optional, Any, cast, Callable, Iterator, List, Dict

import Live
from protocol0.application.constants import PROJECT_ROOT, REMOTE_SCRIPTS_ROOT
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.my_types import T


def scroll_values(items, selected_item, go_next, rotate=True):
    # type: (Iterator[T], Optional[T], bool, bool) -> T
    items_list = list(items)  # type: List[T]
    if selected_item not in items_list:
        selected_item = items_list[0]

    increment = 1 if go_next else -1

    if rotate is False:
        if (selected_item == items_list[0] and increment == -1) \
                or (selected_item == items_list[-1] and increment == 1):
            return selected_item
    try:
        index = (items_list.index(selected_item) + increment) % len(items_list)
        return items_list[index]
    except ValueError:
        return selected_item


def find_if(predicate, seq):
    # type: (Callable[[T], bool], CollectionsSequence[T]) -> Optional[T]
    for x in seq:
        if predicate(x):
            return x
    return None


def get_frame_info(frame_count=1):
    # type: (int) -> Optional[Any]
    call_frame = inspect.currentframe()
    for _ in range(frame_count):
        next_frame = call_frame.f_back
        if not next_frame:
            break
        call_frame = next_frame
    try:
        (filename, line, method_name, _, _) = inspect.getframeinfo(cast(FrameType, call_frame))
    except IndexError:
        return None
    filename = filename.replace(PROJECT_ROOT + "\\", "").replace(REMOTE_SCRIPTS_ROOT + "\\", "")
    class_name = filename.replace(".py", "").split("\\")[-1]

    FrameInfo = namedtuple("FrameInfo", ["filename", "class_name", "line", "method_name"])
    return FrameInfo(filename=filename, class_name=class_name, line=line, method_name=method_name)


def _has_callback_queue(func):
    # type: (Any) -> bool
    """ mixing duck typing and isinstance to ensure we really have a callback handler object """
    from protocol0.domain.sequence.CallbackDescriptor import CallableWithCallbacks
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


def is_lambda(func):
    # type: (Callable) -> bool
    return isinstance(func, types.LambdaType) and func.__name__ == "<lambda>"


def smart_string(s):
    # type: (Any) -> str
    if not isinstance(s, basestring):
        s = str(s)
    return s.decode("utf-8").encode("ascii", "replace")  # type: ignore


def normalize_string(s):
    # type: (basestring) -> str
    return smart_string(s).strip().lower()


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
    # type: (Callable) -> str
    from protocol0.domain.sequence.Sequence import Sequence
    from protocol0.domain.sequence.SequenceStep import SequenceStep
    from protocol0.domain.sequence.CallbackDescriptor import CallableWithCallbacks
    if isinstance(func, Sequence) or isinstance(func, SequenceStep) or isinstance(func, CallableWithCallbacks):
        return func.__repr__()

    decorated_func = get_inner_func(func)
    class_name = get_class_name_from_method(decorated_func)

    if isinstance(decorated_func, CallableWithCallbacks):
        return decorated_func.__repr__()

    if not hasattr(decorated_func, "__name__"):
        return "only class_name %s" % class_name or "unknown"

    if class_name:
        return "%s.%s" % (class_name, decorated_func.__name__)
    else:
        return decorated_func.__name__


def nop(*_, **__):
    # type: (Any, Any) -> None
    pass


def set_device_parameter(param, value):
    # type: (Live.DeviceParameter.DeviceParameter, float) -> None
    if not param.is_enabled:
        return None
    value = max(param.min, value)
    value = min(param.max, value)
    # noinspection PyPropertyAccess
    param.value = value


def class_attributes(cls):
    # type: (Any) -> Dict
    attributes = {}
    for key, value in inspect.getmembers(cls):
        if not key.startswith('_') and not inspect.ismethod(value):
            attributes[key] = value
    return attributes


def compare_values(value, expected_value):
    # type: (Any, Any) -> bool
    if isinstance(value, float):
        value = round(value, 3)
        expected_value = round(expected_value, 3)

    return value == expected_value


def get_length_legend(length):
    # type: (float) -> str
    if length == 0:
        return "unlimited bars"
    from protocol0.domain.lom.song.Song import Song

    if int(length) % Song.get_instance().signature_numerator != 0:
        return "%d beat%s" % (length, "s" if length > 1 else "")
    else:
        bar_length = length / Song.get_instance().signature_numerator
        return "%d bar%s" % (bar_length, "s" if bar_length > 1 else "")