from typing import Any, cast

from protocol0.domain.lom.track.abstract_track.AbstractMatchingTrack import AbstractMatchingTrack


class SimpleAudioMatchingTrack(AbstractMatchingTrack):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioMatchingTrack, self).__init__(*a, **k)
        from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

        self._base_track = cast(SimpleAudioTrack, self._base_track)

    def connect_base_track(self):
        # type: () -> None
        pass
