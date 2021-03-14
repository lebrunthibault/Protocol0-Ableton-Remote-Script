import inspect
import types
from collections import namedtuple

from typing import Optional, Any, List, TYPE_CHECKING

from a_protocol_0.consts import ROOT_DIR, REMOTE_SCRIPTS_DIR

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


def parse_number(num_as_string, default_value=None, min_value=None, max_value=None, is_float=False):
    """ Parses the given string containing a number and returns the parsed number.
    If a parse error occurs, the default_value will be returned. If a min_value or
    max_value is given, the default_value will be returned if the parsed_value is not
    within range. """
    ret_value = default_value
    try:
        parsed_value = float(num_as_string) if is_float else int(num_as_string)
        if min_value is not None and parsed_value < min_value:
            return ret_value
        if max_value is not None and parsed_value > max_value:
            return ret_value
        ret_value = parsed_value
    except Exception:
        pass

    return ret_value


def parse_midi_value(num_as_string, default_value=0):
    """ Returns a MIDI value (range 0 - 127) or the given default value. """
    return parse_number(num_as_string, default_value=default_value, min_value=0, max_value=127)


def parse_midi_channel(num_as_string):
    """ Returns a MIDI channel number (0 - 15) or 0 if parse error. """
    return parse_number(num_as_string, default_value=1, min_value=1, max_value=16) - 1


def scroll_values(items, selected_item, go_next, default=None, return_index=False):
    # type: (List[Any], Optional[Any], bool, Any) -> Optional[Any]
    if len(items) == 0:
        return None
    increment = 1 if go_next else - 1
    index = 0
    if selected_item:
        try:
            index = (items.index(selected_item) + increment) % len(items)
        except ValueError:
            try:
                index = (items.index(default) + increment) % len(items)
            except ValueError:
                pass

    return index if return_index else items[index]


def find_where(predicate, seq):
    return [x for x in seq if predicate(x)]


def find_last(predicate, seq):
    items = find_where(predicate, seq)
    return items[-1] if len(items) else None


def is_equal(val1, val2, delta=0.00001):
    if isinstance(val1, (int, long, float)) and isinstance(val2, (int, long, float)):
        return abs(val1 - val2) < delta
    else:
        return val1 == val2


def have_equal_properties(obj1, obj2, properties):
    for property in properties:
        if not hasattr(obj1, property) or not hasattr(obj2, property) or not is_equal(getattr(obj1, property),
                                                                                      getattr(obj2,
                                                                                              property)):
            return False
    return True


def get_frame_info(frame_count=1):
    # type: (int) -> namedtuple
    try:
        call_frame = inspect.currentframe()
        for _ in range(frame_count):
            call_frame = call_frame.f_back
        (filename, line, method_name, _, _) = inspect.getframeinfo(call_frame)
    except Exception:
        return None

    filename = filename.replace(ROOT_DIR + "\\", "").replace(REMOTE_SCRIPTS_DIR + "\\", "")
    class_name = filename.replace(".py", "").split("\\")[-1]

    FrameInfo = namedtuple('FrameInfo', ['filename', 'class_name', 'line', 'method_name'])
    return FrameInfo(filename=filename, class_name=class_name, line=line, method_name=method_name)


def _has_callback_queue(func):
    """ mixing duck typing and isinstance to ensure we really have a callback handler object """
    from a_protocol_0.utils.callback_descriptor import CallableWithCallbacks
    from _Framework.SubjectSlot import CallableSlotMixin
    return func and hasattr(func, "add_callback") and hasattr(func, "remove_callback") and (
            isinstance(func, CallableWithCallbacks) or isinstance(func, CallableSlotMixin))


def is_method(func):
    spec = inspect.getargspec(func)
    return spec.args and spec.args[0] == 'self'


def is_partial(func):
    return "functools.partial" in str(type(func))


def is_lambda(func):
    return isinstance(func, types.LambdaType) and func.__name__ == "<lambda>"


def get_inner_func(func):
    if hasattr(func, "function"):
        return get_inner_func(func.function)
    if hasattr(func, "func"):  # partial
        return get_inner_func(func.func)
    if hasattr(func, "original_func"):  # partial
        return get_inner_func(func.original_func)
    if hasattr(func, "listener"):
        return get_inner_func(func.listener)

    return func


def get_class_name_from_method(func):
    if hasattr(func, "__self__"):
        return func.__self__.__class__.__name__

    if hasattr(func, "__class__"):
        return func.__class__.__name__

    return None


def get_callable_name(func, obj=None):
    if func is None:
        return "None"

    from a_protocol_0.sequence.Sequence import Sequence
    if isinstance(func, Sequence):
        return str(func.name)

    decorated_func = get_inner_func(func)
    if obj:
        class_name = str(obj) if hasattr(obj, "__repr__") else obj.__class__.__name__
    else:
        class_name = get_class_name_from_method(decorated_func)

    if not hasattr(decorated_func, "__name__"):
        return class_name or "unknown"

    if class_name and all(word not in class_name for word in ["function", "None"]):
        return "%s.%s" % (class_name, decorated_func.__name__)
    else:
        return decorated_func.__name__


def has_arg(func, arg):
    spec = inspect.getargspec(func.func if is_partial(func) else func)
    if is_partial(func):
        return arg in spec.args and arg not in func.keywords.keys()
    else:
        return arg in spec.args


def _arg_count(func):
    # type: (callable) -> int
    """ Note : this is not ideal because we cannot know if the defaults are already set by e.g a partial function
        Thus we could be subtracting twice a parameter, but that's better than to have an outer function setting a mismatched parameter
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
    pass


def flatten(t):
    return [item for sublist in t for item in sublist]


def scale_from_value(value, min_a, max_a, min_b, max_b):
    return float(float((max_b - min_b) * (value - min_a)) / (max_a - min_a)) + min_b
