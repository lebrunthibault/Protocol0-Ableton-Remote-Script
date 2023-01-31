from typing import Optional, cast, Dict

from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.TrackAddedEvent import TrackAddedEvent
from protocol0.domain.lom.track.TrackDisconnectedEvent import TrackDisconnectedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.ext_track.ExtMatchingTrack import ExtMatchingTrack
from protocol0.domain.lom.track.group_track.ext_track.ExtMatchingTrackCreator import \
    ExtMatchingTrackCreator
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackCreatorInterface import \
    MatchingTrackCreatorInterface
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackInterface import (
    MatchingTrackInterface,
)
from protocol0.domain.lom.track.simple_track.SimpleMatchingTrack import SimpleMatchingTrack
from protocol0.domain.lom.track.simple_track.SimpleMatchingTrackCreator import \
    SimpleMatchingTrackCreator
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackFlattenedEvent import \
    SimpleTrackFlattenedEvent
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class MatchingTrackService(object):
    def __init__(self, track_component):
        # type: (TrackCrudComponent) -> None
        self._track_crud_component = track_component
        DomainEventBus.subscribe(TrackAddedEvent, self._on_track_added_event)
        DomainEventBus.subscribe(TrackDisconnectedEvent, self._on_track_disconnected_event)
        DomainEventBus.subscribe(SimpleTrackFlattenedEvent, self._on_simple_track_flattened_event)


    def _on_track_added_event(self, _):
        # type: (TrackAddedEvent) -> None
        matching_track = self._create_matching_track(Song.current_track())

        if matching_track is None:
            return

        Scheduler.defer(matching_track.router.monitor_base_track)

        if not Song.is_track_recording():
            Song.current_track().arm_state.arm()

    def bounce_current_track(self):
        # type: () -> Sequence
        current_track = Song.current_track()
        assert isinstance(
            current_track, (ExternalSynthTrack, SimpleMidiTrack)
        ), "Can only bounce midi and ext tracks"

        matching_track = self._create_matching_track(current_track)

        if matching_track is not None and len(list(matching_track._audio_track.devices)) != 0:
            return matching_track.bounce()

        seq = Sequence()

        if matching_track is not None:
            seq.add(matching_track.track_manager.remove_audio_track)

        seq.add(self._create_matching_track_creator(current_track).bounce)
        return seq.done()

    def _create_matching_track(self, track):
        # type: (AbstractTrack) -> Optional[MatchingTrackInterface]
        try:
            if isinstance(track, ExternalSynthTrack):
                return ExtMatchingTrack(track.base_track)
            elif isinstance(track, SimpleTrack):
                return SimpleMatchingTrack(track)
        except AssertionError:
            return None

        return None

    def _create_matching_track_creator(self, track):
        # type: (AbstractTrack) -> Optional[MatchingTrackCreatorInterface]
        if isinstance(track, ExternalSynthTrack):
            return ExtMatchingTrackCreator(self._track_crud_component, track.base_track)
        elif isinstance(track, SimpleTrack):
            return SimpleMatchingTrackCreator(self._track_crud_component, track)

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
                # Here the clip info origin can be either a midi or audio track
                # in case of an audio track, this means bouncing an external synth track
                # the clip info file paths are normally already mapped to midi hashes
                # except in the special case of a legacy track where the mapping has not been
                # done and persisted to the track data
                # (in this case an exception will be raised)
                flattened_track.audio_to_midi_clip_mapping.register_file_path(clip.file_path, clip_info)

        if matching_track is None:
            return None

        return matching_track.clip_manager.broadcast_clips(flattened_track, clip_infos)

    def _on_track_disconnected_event(self, event):
        # type: (TrackDisconnectedEvent) -> None
        matching_track = self._create_matching_track(event.track)
        if matching_track:
            matching_track.router.monitor_audio_track()

    def match_clip_colors(self):
        # type: () -> None
        matching_track = self._create_matching_track(Song.current_track())

        if matching_track is None:
            return

        matching_track.clip_color_manager.toggle_clip_colors()
