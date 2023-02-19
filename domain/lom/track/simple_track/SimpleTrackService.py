from protocol0.domain.lom.track.simple_track.SimpleTrackFlattenedEvent import \
    SimpleTrackFlattenedEvent
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song


class SimpleTrackService(object):
    def __init__(self):
        # type: () -> None
        DomainEventBus.subscribe(SimpleTrackFlattenedEvent, self._on_simple_track_flattened_event)

    def _on_simple_track_flattened_event(self, event):
        # type: (SimpleTrackFlattenedEvent) -> None
        clip_infos = event.clip_infos
        flattened_track = Song.selected_track(SimpleAudioTrack)

        assert len(flattened_track.clips) == len(
            clip_infos
        ), "length mismatch between audio clips: len(clips) == %s, len(clip_infos) == %s" % (
            len(flattened_track.clips),
            len(clip_infos),
        )
        for clip, clip_info in zip(flattened_track.clips, clip_infos):
            clip.looping = True

        flattened_track._needs_flattening = False
