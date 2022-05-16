from functools import partial

from typing import Optional

from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import \
    ExternalSynthTrack
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
        if not isinstance(current_track, ExternalSynthTrack):
            raise Protocol0Warning("Can only show automation of ExternalSynthTrack")

        if len(current_track.dummy_tracks) == 0:
            raise Protocol0Warning("Current track has not dummy track")

        track = current_track.dummy_tracks[0]
        clip = track.clip_slots[SongFacade.selected_scene().index].clip
        if clip is None:
            raise Protocol0Warning("Selected scene has no dummy clip")

        seq = Sequence()
        seq.add(track.select)
        seq.add(partial(clip.automation.scroll_envelopes, track.devices.parameters))
        return seq.done()
