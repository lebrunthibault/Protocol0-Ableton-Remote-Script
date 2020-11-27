from abc import ABCMeta

from typing import TYPE_CHECKING, Optional
import Live

from a_protocol_0.actions.AhkCommands import AhkCommands
from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Song import Song
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component


class AbstractInstrument(object):
    __metaclass__ = ABCMeta
    NUMBER_OF_PRESETS = 128

    def __init__(self, simple_track):
        # type: (Optional["SimpleTrack"]) -> None
        self.track = simple_track
        self.track.instrument = self
        self.is_null = False
        self.browser = Live.Application.get_application().browser
        self._cached_browser_items = {}
        self.needs_activation = False
        self.editor_track = "midi"

    def __nonzero__(self):
        return not self.is_null

    @property
    def song(self):
        # type: () -> Song
        return self.track.song

    @property
    def parent(self):
        # type: () -> "Protocol0Component"
        return self.song.parent

    @property
    def name(self):
        # type: () -> str
        return type(self).__name__

    def action_show(self):
        # type: () -> None
        AhkCommands.select_first_vst()

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> None
        if self.track.preset_index == -1:
            new_preset_index = 0
        else:
            new_preset_index = self.track.preset_index + 1 if go_next else self.track.preset_index - 1
        new_preset_index %= self.NUMBER_OF_PRESETS

        self.track.name = TrackName(self.track).get_track_name_for_preset_index(new_preset_index)

        self.set_preset(new_preset_index)

    def set_preset(self, preset_index):
        # type: (int) -> None
        """ default is send program change """
        self.parent.midi.send_program_change(preset_index)
