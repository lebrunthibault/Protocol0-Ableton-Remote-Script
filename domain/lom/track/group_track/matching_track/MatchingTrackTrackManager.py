from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.shared.sequence.Sequence import Sequence


class MatchingTrackTrackManager(object):
    def __init__(self, base_track, audio_track):
        # type: (SimpleTrack, SimpleAudioTrack) -> None
        self._base_track = base_track
        self._audio_track = audio_track

    def remove_audio_track(self):
        # type: () -> Sequence
        self._base_track.output_routing.track = self._audio_track.output_routing.track   # type: ignore

        return self._audio_track.delete()