import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.utils.timing import defer


class MatchingTrackSoloState(SlotManager):
    def __init__(self, base_track, audio_track):
        # type: (SimpleTrack, SimpleAudioTrack) -> None
        super(MatchingTrackSoloState, self).__init__()
        self._base_track = base_track
        self._audio_track = audio_track
        self._solo_listener.replace_subjects([self._base_track._track, self._audio_track._track])

    @subject_slot_group("solo")
    @defer
    def _solo_listener(self, track):
        # type: (Live.Track.Track) -> None
        self._base_track.solo = track.solo
        self._audio_track.solo = track.solo
