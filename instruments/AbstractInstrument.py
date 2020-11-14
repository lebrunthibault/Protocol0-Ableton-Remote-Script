from abc import ABCMeta, abstractmethod

from typing import TYPE_CHECKING
import Live

from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.actions.AbstractUserAction import AbstractUserAction


class AbstractInstrument(object):
    __metaclass__ = ABCMeta

    NUMBER_OF_PRESETS = 128

    def __init__(self, simple_track):
        # type: ("SimpleTrack") -> None
        self.track = simple_track
        self.is_null = False
        self.browser = Live.Application.get_application().browser
        self._cached_browser_items = {}

    def __nonzero__(self):
        return not self.is_null

    @property
    def song(self):
        # type: () -> Song
        return self.track.song

    @property
    def parent(self):
        # type: () -> AbstractUserAction
        return self.song.parent

    @property
    def name(self):
        # type: () -> str
        return type(self).__name__

    @abstractmethod
    def action_show(self):
        # type: () -> None
        pass

    @abstractmethod
    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> str
        pass

    def action_scroll_via_program_change(self, go_next):
        # type: (bool) -> str
        if self.track.preset_index == -1:
            new_preset_index = 0
        else:
            new_preset_index = self.track.preset_index + 1 if go_next else self.track.preset_index - 1
        new_preset_index = new_preset_index % self.NUMBER_OF_PRESETS

        self.track.name = TrackName(self.track).get_track_name_for_preset_index(new_preset_index)

        Live.Browser.Browser.load_item()
        return "; midi pc 1 {0}".format(new_preset_index)
