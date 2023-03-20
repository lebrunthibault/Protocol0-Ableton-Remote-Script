from functools import partial

from typing import Optional, cast

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class TrackAutomationService(object):
    def __init__(self, track_factory):
        # type: (TrackFactory) -> None
        self._track_factory = track_factory
        self._last_selected_parameter = None  # type: Optional[DeviceParameter]
        self._last_scrolled_parameter = None  # type: Optional[DeviceParameter]

    def show_automation(self, go_next):
        # type: (bool) -> Sequence
        selected_parameter = Song.selected_parameter() or self._last_scrolled_parameter

        seq = Sequence()

        if selected_parameter is not None:
            seq.add(partial(self._show_selected_parameter_automation, selected_parameter))
        else:
            seq.add(partial(self._scroll_automated_parameters, go_next))

        return seq.done()

    def _show_selected_parameter_automation(self, selected_parameter):
        # type: (DeviceParameter) -> None
        if selected_parameter not in Song.selected_track().devices.parameters:
            self._last_scrolled_parameter = None
            raise Protocol0Warning("parameter does not belong to selected track")

        self._last_scrolled_parameter = selected_parameter
        Song.selected_clip().automation.show_parameter_envelope(selected_parameter)

    def _scroll_automated_parameters(self, go_next):
        # type: (bool) -> Sequence
        """Scroll the automated parameters of the clip"""
        from protocol0.shared.logging.Logger import Logger
        Logger.dev("scrolling")
        current_track = Song.current_track()
        index = Song.selected_scene().index

        automated_parameters = current_track.get_automated_parameters(index)

        if len(automated_parameters.items()) == 0:
            raise Protocol0Warning("No automated parameters")

        selected_parameter = ValueScroller.scroll_values(
            automated_parameters.keys(), self._last_selected_parameter, go_next
        )
        track = automated_parameters[selected_parameter]

        seq = Sequence()
        seq.add(track.select)
        seq.add(
            partial(
                track.clip_slots[index].clip.automation.show_parameter_envelope, selected_parameter
            )
        )
        self._last_selected_parameter = selected_parameter
        return seq.done()

    def select_or_sync_automation(self):
        # type: () -> None
        """
        Either we have a midi clip focused and we sync the automation (rev2) layers
        Or we create a new automation lane for the selected parameter
        """
        current_track = Song.current_track()
        selected_track = Song.selected_track()

        if (
            isinstance(current_track, ExternalSynthTrack)
            and selected_track == current_track.midi_track
        ):
            Song.selected_clip(MidiClip).synchronize_automation_layers(
                Song.selected_track().devices.parameters
            )
        else:
            self._create_automation_from_selected_parameter()

    def _create_automation_from_selected_parameter(self):
        # type: () -> Sequence
        selected_track = Song.selected_track()
        selected_clip = selected_track.clip_slots[Song.selected_scene().index].clip
        selected_parameter = Song.selected_parameter()

        if selected_parameter is None:
            raise Protocol0Warning("No selected parameter")

        seq = Sequence()
        if selected_clip is None:
            raise Protocol0Warning("No selected clip")

        seq.add(
            lambda: Song.selected_clip().automation.select_or_create_envelope(
                cast(DeviceParameter, selected_parameter)
            )
        )

        return seq.done()
