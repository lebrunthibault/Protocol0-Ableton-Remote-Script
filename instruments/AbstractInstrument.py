from abc import ABCMeta, abstractproperty, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack


class AbstractInstrument(object):
    __metaclass__ = ABCMeta

    def __init__(self, simple_track):
        # type: ("SimpleTrack") -> None
        self.track = simple_track
        self.is_null = False

    def __nonzero__(self):
        return not self.is_null

    @abstractproperty
    def action_show(self):
        # type: () -> str
        pass

    @abstractmethod
    def action_scroll_preset_or_sample(self, go_next):
        # type: (bool) -> str
        pass