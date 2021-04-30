from typing import Optional, Any, TYPE_CHECKING

from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class ExternalSynthTrackName(TrackName):
    def __init__(self, track, *a, **k):
        # type: (ExternalSynthTrack, Any, Any) -> None
        super(ExternalSynthTrackName, self).__init__(track, *a, **k)
        self.track = track

    def update(self, base_name=None):
        # type: (Optional[str]) -> None
        super(ExternalSynthTrackName, self).update(base_name=base_name)
        self.track.midi_track.track_name.update(base_name="midi")
        self.track.audio_track.track_name.update(base_name="audio")
