from protocol0.domain.lom.track.simple_track.SimpleTrackFlattenedEvent import \
    SimpleTrackFlattenedEvent
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song


class SimpleTrackService(object):
    def __init__(self):
        # type: () -> None
        DomainEventBus.subscribe(SimpleTrackFlattenedEvent, self._on_simple_track_flattened_event)

    def _on_simple_track_flattened_event(self, _):
        # type: (SimpleTrackFlattenedEvent) -> None
        flattened_track = Song.selected_track(SimpleAudioTrack)

        for clip in flattened_track.clips:
            clip.looping = True
            clip.loop.start = 0
            clip.loop.end = clip.loop.end / 2

        flattened_track._needs_flattening = False
