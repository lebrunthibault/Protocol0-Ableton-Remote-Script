import inspect
import types
from collections import namedtuple
from functools import partial as _partial
from itertools import chain, imap
from typing import Optional, Any, List, Union, TYPE_CHECKING

import Live

from a_protocol_0.consts import PROTOCOL0_FOLDER, REMOTE_SCRIPTS_FOLDER

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


def scroll_values(items, selected_item, go_next, default=None):
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

    return items[index]


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


def compare_properties(obj1, obj2, properties):
    for property in properties:
        if not hasattr(obj1, property) or not hasattr(obj2, property) or not is_equal(getattr(obj1, property),
                                                                                      getattr(obj2,
                                                                                              property)):
            return False
    return True


def find_all_devices(track, only_visible=False):
    # type: (AbstractTrack, bool) -> List[Live.Device.Device]
    return _find_all_devices(track_or_chain=track._track, only_visible=only_visible)


def _find_all_devices(track_or_chain, only_visible=False):
    # type: (Union[Live.Track.Track, Live.Chain.Chain], bool) -> List[Live.Device.Device]
    u""" Returns a list with all devices from a track or chain """
    devices = []
    for device in filter(None, track_or_chain.devices):  # type: Live.Device.Device
        if only_visible and device.view.is_collapsed:
            devices += [device]
            continue
        if only_visible and (
                not device.can_have_drum_pads and device.can_have_chains and device.view.is_showing_chain_devices):
            devices += chain([device], _find_all_devices(device.view.selected_chain, only_visible=only_visible))
        elif not device.can_have_drum_pads and isinstance(device, Live.RackDevice.RackDevice):
            devices += chain([device],
                             *imap(_partial(_find_all_devices, only_visible=only_visible), filter(None, device.chains)))
        else:
            devices += [device]
    return devices


def get_frame_info(frame_count=1):
    # type: (int) -> namedtuple
    try:
        call_frame = inspect.currentframe()
        for _ in range(frame_count):
            call_frame = call_frame.f_back
        (filename, line, method_name, _, _) = inspect.getframeinfo(call_frame)
    except Exception:
        return None

    filename = filename.replace(PROTOCOL0_FOLDER + "\\", "").replace(REMOTE_SCRIPTS_FOLDER + "\\", "")
    class_name = filename.replace(".py", "").split("\\")[-1]

    FrameInfo = namedtuple('FrameInfo', ['filename', 'class_name', 'line', 'method_name'])
    return FrameInfo(filename=filename, class_name=class_name, line=line, method_name=method_name)


def _has_callback_queue(func):
    return hasattr(func, "_has_callback_queue") and hasattr(func, "_callbacks")


def is_method(func):
    spec = inspect.getargspec(func)
    return spec.args and spec.args[0] == 'self'


def is_partial(func):
    return str(type(func)) == "<type 'functools.partial'>"


def is_lambda(func):
    return isinstance(func, types.LambdaType) and func.__name__ == "<lambda>"


def get_callable_decorated_func(func):
    if hasattr(func, "function"):
        return get_callable_decorated_func(func.function)
    if hasattr(func, "func"):  # partial
        return get_callable_decorated_func(func.func)

    return func


def get_class_name_from_method(func):
    if hasattr(func, "__self__"):
        return func.__self__.__class__.__name__

    if hasattr(func, "__class__"):
        return func.__class__.__name__

    return None


def get_callable_name(func):
    if func is None:
        return "None"
    from a_protocol_0.sequence.Sequence import Sequence
    if isinstance(func, Sequence):
        return str(func.name)

    decorated_func = get_callable_decorated_func(func)
    class_name = get_class_name_from_method(func)

    if not hasattr(decorated_func, "__name__"):
        return class_name or "unknown"

    if class_name:
        return "%s.%s" % (class_name, decorated_func.__name__)
    else:
        return decorated_func.__name__


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
