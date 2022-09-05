from functools import partial

from typing import Optional, cast

from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class TrackAutomationService(object):
    def __init__(self, track_factory):
        # type: (TrackFactory) -> None
        self._track_factory = track_factory
        self._last_selected_parameter = None  # type: Optional[DeviceParameter]

    def show_automation(self, go_next):
        # type: (bool) -> Optional[Sequence]
        selected_parameter = SongFacade.selected_parameter()
        if selected_parameter is not None:
            return self._show_selected_parameter_automation(selected_parameter)
        else:
            return self._scroll_automated_parameters(go_next)

    def _show_selected_parameter_automation(self, selected_parameter):
        # type: (DeviceParameter) -> Optional[Sequence]
        # check if its a return or not
        current_track = SongFacade.current_track()
        selected_track = SongFacade.selected_track()

        # simple access
        if not isinstance(current_track, AbstractGroupTrack) or isinstance(
            selected_track, SimpleMidiExtTrack
        ):
            SongFacade.selected_clip().automation.show_parameter_envelope(selected_parameter)
            return None

        # Special case if we clicked by mistake on a send parameter of any sub track
        # consider we wanted to show the automation of the dummy return track instead
        if selected_parameter.is_mixer_parameter:  # type: ignore[unreachable]
            (
                selected_track,
                selected_parameter,
            ) = current_track.dummy_group.get_selected_mixer_parameter(selected_parameter)

        if not isinstance(selected_track, SimpleDummyTrack):
            Backend.client().show_warning("Can only show automation on dummy tracks")

        selected_clip = selected_track.clip_slots[SongFacade.selected_scene().index].clip
        if selected_clip is None:
            clip = "dummy return clip" if selected_parameter.is_mixer_parameter else "dummy clip"
            raise Protocol0Warning("Selected scene has no %s" % clip)

        seq = Sequence()
        seq.add(selected_track.select)
        seq.add(partial(selected_clip.automation.show_parameter_envelope, selected_parameter))
        return seq.done()

    def _scroll_automated_parameters(self, go_next):
        # type: (bool) -> Sequence
        """Scroll the automated parameters of the dummy clips"""
        current_track = SongFacade.current_track()
        index = SongFacade.selected_scene().index
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
            self._create_automation_from_selected_parameter()

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
