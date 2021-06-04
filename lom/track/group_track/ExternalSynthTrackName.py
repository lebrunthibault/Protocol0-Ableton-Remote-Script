from typing import Optional, Any, TYPE_CHECKING

from a_protocol_0.lom.track.AbstractTrackName import AbstractTrackName

if TYPE_CHECKING:
    from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class ExternalSynthTrackName(AbstractTrackName):
    def __init__(self, track, *a, **k):
        # type: (ExternalSynthTrack, Any, Any) -> None
        super(ExternalSynthTrackName, self).__init__(track, *a, **k)
        self.track = track

    def update(self, base_name=None, *a, **k):
        # type: (Optional[str], Any, Any) -> None
        super(ExternalSynthTrackName, self).update(base_name=base_name, *a, **k)
        self.track.midi_track.track_name.update(base_name="midi", *a, **k)
        self.track.audio_track.track_name.update(base_name="audio", *a, **k)
