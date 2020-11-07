from abc import ABCMeta, abstractproperty, abstractmethod

from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack


class AbstractInstrument(object):
    __metaclass__ = ABCMeta

    NUMBER_OF_PRESETS = 128

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

    def action_scroll_via_program_change(self, go_next):
        # type: (bool) -> str
        if self.track.preset_index == -1:
            new_preset_index = 0
        else:
            new_preset_index = self.track.preset_index + 1 if go_next else self.track.preset_index - 1
        new_preset_index = new_preset_index % self.NUMBER_OF_PRESETS

        action_list = "; midi pc 1 {0}".format(new_preset_index)
        action_list += "; {0}/name '{1}'".format(self.track.index,
                                                 TrackName(self.track).get_track_name_for_preset_index(new_preset_index))

        return action_list
