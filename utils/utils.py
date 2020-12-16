from itertools import chain, imap
from typing import Optional, Any, List

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


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


def scroll_values(items, selected_item, go_next):
    # type: (List[Any], Optional[Any], bool) -> Optional[Any]
    if len(items) == 0:
        return None
    increment = 1 if go_next else - 1
    if not selected_item:
        index = 1
    else:
        index = (items.index(selected_item) + increment) % len(items)

    return items[index]


def find_where(predicate, seq):
    return [x for x in seq if predicate(x)]


def find_last(predicate, seq):
    items = find_where(predicate, seq)
    return items[-1] if len(items) else None


def find_all_devices(track_or_chain):
    # type: (Any) -> List[Any]
    u"""
    Returns a list with all devices from a track or chain.
    """
    if track_or_chain:
        devices = []
        for device in track_or_chain.devices:
            if device:
                if not device.can_have_drum_pads and device.can_have_chains:
                    devices += chain([device], *imap(find_all_devices, device.chains))
                else:
                    devices += [device]
        return devices
    return []
