from functools import partial

from typing import Optional, cast

from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class TrackAutomationService(object):
    def __init__(self, track_factory):
        # type: (TrackFactory) -> None
        self._track_factory = track_factory

    def show_automation(self):
        # type: () -> Optional[Sequence]
        selected_parameter = SongFacade.selected_parameter()
        if selected_parameter and SongFacade.selected_clip_slot().clip:
            SongFacade.selected_clip().automation.show_parameter_envelope(selected_parameter)
            return None

        current_track = SongFacade.current_track()
        # following behavior is only for group tracks
        if not isinstance(current_track, AbstractGroupTrack):
            if selected_parameter is None:
                raise Protocol0Warning("no selected parameter")
            else:
                raise Protocol0Warning("no selected clip")

        dummy_tracks = list(
            filter(None, (current_track.dummy_track, current_track.dummy_return_track))
        )
        if len(dummy_tracks) == 0:
            raise Protocol0Warning("Current track has no dummy track")

        # noinspection PyTypeChecker
        dummy_track = cast(
            SimpleDummyTrack,
            ValueScroller.scroll_values(dummy_tracks, SongFacade.selected_track(), True),
        )
        clip = dummy_track.selected_clip_slot.clip
        if clip is None:
            raise Protocol0Warning("Selected scene has no dummy clip")

        seq = Sequence()
        seq.add(dummy_track.select)
        seq.add(partial(clip.automation.scroll_envelopes, dummy_track.devices.parameters))
        return seq.done()

    def select_or_sync_automation(self):
        # type: () -> None
        """
        Either we have a midi clip focused and we sync the automation (prophet) layers
        Or we create a new automation lane for the selected parameter
        """
        current_track = SongFacade.current_track()
        selected_track = SongFacade.selected_track()

        if (
            isinstance(current_track, ExternalSynthTrack)
            and selected_track == current_track.midi_track
        ):
            SongFacade.selected_midi_clip().synchronize_automation_layers(
                SongFacade.selected_track().devices.parameters
            )
        else:
            self._create_automation_from_selected_parameter

    @property
    def _create_automation_from_selected_parameter(self):
        # type: () -> Sequence
        selected_track = SongFacade.selected_track()
        selected_clip = selected_track.selected_clip_slot.clip
        selected_parameter = SongFacade.selected_parameter()

        if selected_parameter is None:
            raise Protocol0Warning("No selected parameter")

        seq = Sequence()
        if selected_clip is None:
            if isinstance(selected_track, SimpleDummyTrack):
                seq.add(selected_track.automation.insert_dummy_clip)
            else:
                raise Protocol0Warning("No selected clip")

        seq.add(
            lambda: SongFacade.selected_clip().automation.select_or_create_envelope(
                cast(DeviceParameter, selected_parameter)
            )
        )

        return seq.done()
