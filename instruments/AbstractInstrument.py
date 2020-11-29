from abc import ABCMeta
from typing import TYPE_CHECKING, Any

import Live

from a_protocol_0.consts import GROUP_PROPHET_NAME, GROUP_MINITAUR_NAME
from a_protocol_0.lom.track.TrackName import TrackName, AbstractObject

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Song import Song
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component


class AbstractInstrument(AbstractObject):
    __metaclass__ = ABCMeta
    NUMBER_OF_PRESETS = 128

    def __init__(self, simple_track, *a, **k):
        # type: ("SimpleTrack", Any, Any) -> None
        super(AbstractInstrument, self).__init__(*a, **k)
        self.track = simple_track
        self.track.instrument = self
        self.is_null = False
        self.browser = Live.Application.get_application().browser
        self._cached_browser_items = {}
        self.needs_activation = False
        self.can_be_shown = True
        self.has_rack = False

    def __nonzero__(self):
        return not self.is_null

    @staticmethod
    def create_from_abstract_track(track):
        # type: ("AbstractTrack") -> AbstractInstrument
        from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
        from a_protocol_0.lom.track.GroupTrack import GroupTrack
        from a_protocol_0.instruments.InstrumentMinitaur import InstrumentMinitaur
        from a_protocol_0.instruments.InstrumentNull import InstrumentNull
        from a_protocol_0.instruments.InstrumentProphet import InstrumentProphet
        from a_protocol_0.instruments.InstrumentSerum import InstrumentSerum
        from a_protocol_0.instruments.InstrumentSimpler import InstrumentSimpler

        if isinstance(track, SimpleTrack):
            if track.is_simpler:
                return InstrumentSimpler(track)
            if len(track.devices) and "serum" in track.devices[0].name.lower():
                return InstrumentSerum(track)
            else:
                return InstrumentNull(track)

        if isinstance(track, GroupTrack):
            if track.name == GROUP_PROPHET_NAME:
                return InstrumentProphet(track.selectable_track)
            if track.name == GROUP_MINITAUR_NAME:
                return InstrumentMinitaur(track.selectable_track)
            else:
                raise Exception("Invalid GroupTrack name")

    @property
    def song(self):
        # type: () -> Song
        return self.track.song

    @property
    def name(self):
        # type: () -> str
        return type(self).__name__

    def activate(self):
        # type: () -> None
        """ for instruments needing gui click activation """
        pass

    def show(self):
        # type: () -> None
        if self.has_rack:
            self.parent.ahk_commands.toggle_first_vst_with_rack()
        else:
            self.parent.ahk_commands.toggle_first_vst()

    def action_scroll_presets_or_samples(self, go_next):
        # type: (bool) -> None
        if self.track.preset_index == -1:
            new_preset_index = 0
        else:
            new_preset_index = self.track.preset_index + 1 if go_next else self.track.preset_index - 1
        new_preset_index %= self.NUMBER_OF_PRESETS

        self.track.name = TrackName(self.track).get_track_name_for_preset_index(new_preset_index)

        self.set_preset(new_preset_index, go_next)

    def set_preset(self, preset_index, _):
        # type: (int, bool) -> None
        """ default is send program change """
        self.parent.midi.send_program_change(preset_index)
