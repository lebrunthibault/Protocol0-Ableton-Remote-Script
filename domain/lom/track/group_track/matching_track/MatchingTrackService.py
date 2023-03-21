from typing import Optional, cast, Dict

from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.TrackAddedEvent import TrackAddedEvent
from protocol0.domain.lom.track.TrackDisconnectedEvent import TrackDisconnectedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.NormalGroupMatchingTrack import NormalGroupMatchingTrack
from protocol0.domain.lom.track.group_track.NormalGroupMatchingTrackCreator import (
    NormalGroupMatchingTrackCreator,
)
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.group_track.ext_track.ExtMatchingTrack import ExtMatchingTrack
from protocol0.domain.lom.track.group_track.ext_track.ExtMatchingTrackCreator import (
    ExtMatchingTrackCreator,
)
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackCreatorInterface import (
    MatchingTrackCreatorInterface,
)
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackInterface import (
    MatchingTrackInterface,
)
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleMatchingTrack import SimpleMatchingTrack
from protocol0.domain.lom.track.simple_track.SimpleMatchingTrackCreator import (
    SimpleMatchingTrackCreator,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackFlattenedEvent import (
    SimpleTrackFlattenedEvent,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class MatchingTrackService(object):
    def __init__(self, track_component):
        # type: (TrackCrudComponent) -> None
        self._track_crud_component = track_component
        DomainEventBus.subscribe(TrackAddedEvent, self._on_track_added_event)
        DomainEventBus.subscribe(TrackDisconnectedEvent, self._on_track_disconnected_event)
        DomainEventBus.subscribe(SimpleTrackFlattenedEvent, self._on_simple_track_flattened_event)

        Scheduler.defer(self._generate_clip_hashes)

    def _generate_clip_hashes(self):
        # type: () -> None
        for track in Song.abstract_tracks():
            matching_track = self._create_matching_track(track)

            if matching_track is not None:
                Logger.info("init clips of %s" % track)
                matching_track.init_clips()

    def _on_track_added_event(self, _):
        # type: (TrackAddedEvent) -> None
        matching_track = self._create_matching_track(Song.current_track())

        if matching_track is None:
            return

        Scheduler.defer(matching_track.router.monitor_base_track)

        matching_track.init_clips()

        if not Song.is_track_recording():
            Song.current_track().arm_state.arm()

    def bounce_current_track(self):
        # type: () -> Optional[Sequence]
        current_track = Song.current_track()

        matching_track = self._create_matching_track(current_track)

        if matching_track is not None:
            return matching_track.bounce()

        return self._create_matching_track_creator(current_track).bounce()

    def _create_matching_track(self, track):
        # type: (AbstractTrack) -> Optional[MatchingTrackInterface]
        try:
            if isinstance(track, SimpleTrack):
                return SimpleMatchingTrack(track)
            if isinstance(track, ExternalSynthTrack):
                return ExtMatchingTrack(track.base_track)
            elif isinstance(track, NormalGroupTrack):
                return NormalGroupMatchingTrack(track.base_track)
        except AssertionError:
            return None

        return None

    def _create_matching_track_creator(self, track):
        # type: (AbstractTrack) -> Optional[MatchingTrackCreatorInterface]
        if isinstance(track, SimpleTrack):
            return SimpleMatchingTrackCreator(self._track_crud_component, track)
        elif isinstance(track, ExternalSynthTrack):
            return ExtMatchingTrackCreator(self._track_crud_component, track.base_track)
        elif isinstance(track, NormalGroupTrack):
            return NormalGroupMatchingTrackCreator(self._track_crud_component, track.base_track)

        return None

    def _on_simple_track_flattened_event(self, event):
        # type: (SimpleTrackFlattenedEvent) -> Optional[Sequence]
        clip_infos = event.clip_infos
        flattened_track = Song.selected_track(SimpleAudioTrack)

        # update the clip mapping
        clip_info_by_index = cast(Dict[int, ClipInfo], {c.index: c for c in clip_infos})

        # this links the flattened track with the optional audio track
        matching_track = self._create_matching_track(flattened_track.abstract_track)

        # then we update the shared audio_to_midi_clip_mapping
        for clip in flattened_track.clips:
            if clip.index in clip_info_by_index:
                clip_info = clip_info_by_index[clip.index]  # noqa
                # Here the clip info origin is linked to the new clip
                flattened_track.clip_mapping.register_file_path(clip.file_path, clip_info)

        if matching_track is None:
            return None

        return matching_track.clip_manager.broadcast_clips(flattened_track, clip_infos)

    def _on_track_disconnected_event(self, event):
        # type: (TrackDisconnectedEvent) -> None
        matching_track = self._create_matching_track(event.track)

        if matching_track is not None:
            matching_track.router.monitor_audio_track()
        else:
            for track in Song.simple_tracks():
                if (
                    track != event.track
                    and liveobj_valid(track._track)
                    and not track.is_foldable
                    and track.name == event.track.name
                    and track.index > event.track.index
                    and track.output_routing.type == OutputRoutingTypeEnum.SENDS_ONLY
                ):
                    track.output_routing.track = track.group_track or Song.master_track()  # type: ignore[assignment]

                    # seq = Sequence()
                    # seq.prompt("Remove saved track '%s'?" % track.name)
                    # seq.add(partial(Backend.client().delete_saved_track, track.name))
                    # seq.done()

    def match_clip_colors(self):
        # type: () -> None
        matching_track = self._create_matching_track(Song.current_track())

        if matching_track is None:
            return

        matching_track.clip_color_manager.toggle_clip_colors()
