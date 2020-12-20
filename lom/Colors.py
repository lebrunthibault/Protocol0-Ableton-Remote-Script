from typing import Optional

from _Framework.Util import find_if
from a_protocol_0.consts import EXTERNAL_SYNTH_PROPHET_NAME, EXTERNAL_SYNTH_MINITAUR_NAME


class Colors(object):
    SELECTED = 7
    ARM = 14
    DISABLED = 13

    _dynamic_names = {
        EXTERNAL_SYNTH_PROPHET_NAME: 23,
        EXTERNAL_SYNTH_MINITAUR_NAME: 69
    }

    @staticmethod
    def get(key, default=13):
        # type: (str, Optional[int]) -> int
        track_type = find_if(lambda name: name in key, Colors._dynamic_names)
        return Colors._dynamic_names[track_type] if track_type else default
