from typing import Any

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class ResamplingTrack(SimpleTrack):
    TRACK_NAME = "Resampling"

    def stop(self, *a, **k):
        # type: (Any, Any) -> None
        if self.is_recording:
            return

        super(ResamplingTrack, self).stop(*a, **k)
