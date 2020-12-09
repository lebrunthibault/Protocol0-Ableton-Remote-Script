from typing import Optional

from a_protocol_0.consts import EXTERNAL_SYNTH_PROPHET_NAME, EXTERNAL_SYNTH_MINITAUR_NAME


class Colors(object):
    SELECTED = 7
    ARM = 14
    DISABLED = 13

    @staticmethod
    def has(key):
        # type: (str) -> bool
        return hasattr(Colors, key)

    @staticmethod
    def get(key, default=13):
        # type: (str, Optional[int]) -> int
        return getattr(Colors, key) if Colors.has(key) else default


setattr(Colors, EXTERNAL_SYNTH_PROPHET_NAME, 23)
setattr(Colors, EXTERNAL_SYNTH_MINITAUR_NAME, 69)
