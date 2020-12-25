import inspect
import types
from functools import partial as _partial
from itertools import chain, imap
from math import ceil
from typing import Optional, Any, List, Union, TYPE_CHECKING

import Live

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent

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


class Utils(AbstractControlSurfaceComponent):

    def get_beat_time(self, bar_count=1):
        """ Returns the absolute beat time to use based on the given bar_count arg and current time
        signature of the song """
        beat = 4.0 / self.song._song.signature_denominator
        num = parse_number(bar_count, min_value=0, default_value=1, is_float=True)
        return beat * self.song._song.signature_numerator * num

    def get_next_quantized_position(self, position, length):
        # type: (float, float) -> float
        """ Use clip_trigger_quantization if the quantization is variable """
        return (ceil((position % length) / 4) * 4) % length


def scroll_values(items, selected_item, go_next):
    # type: (List[Any], Optional[Any], bool) -> Optional[Any]
    if len(items) == 0:
        return None
    increment = 1 if go_next else - 1
    index = 0
    if selected_item:
        try:
            index = (items.index(selected_item) + increment) % len(items)
        except ValueError:
            pass

    return items[index]


def find_where(predicate, seq):
    return [x for x in seq if predicate(x)]


def find_last(predicate, seq):
    items = find_where(predicate, seq)
    return items[-1] if len(items) else None


def find_all_devices(track, only_visible=False):
    # type: (AbstractTrack, bool) -> List[Live.Device.Device]
    return _find_all_devices(track_or_chain=track._track, only_visible=only_visible)


def _find_all_devices(track_or_chain, only_visible=False):
    # type: (Union[Live.Track.Track, Live.Chain.Chain], bool) -> List[Live.Device.Device]
    u""" Returns a list with all devices from a track or chain """
    devices = []
    for device in filter(None, track_or_chain.devices):
        if only_visible and device.view.is_collapsed:
            devices += [device]
            continue
        if only_visible and (
                not device.can_have_drum_pads and device.can_have_chains and device.view.is_showing_chain_devices):
            devices += chain([device], _find_all_devices(device.view.selected_chain, only_visible=only_visible))
        elif not device.can_have_drum_pads and device.can_have_chains:
            devices += chain([device],
                             *imap(_partial(_find_all_devices, only_visible=only_visible), filter(None, device.chains)))
        else:
            devices += [device]
    return devices


def _arg_count(func):
    # type: (callable) -> int
    arg_len = len(inspect.getargspec(func).args)
    return arg_len if isinstance(func, types.FunctionType) else arg_len - 1
