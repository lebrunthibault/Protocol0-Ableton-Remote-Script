import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackProxy import MatchingTrackProxy
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.observer.Observable import Observable


class MatchingTrackSoloState(SlotManager):
    def __init__(self, track_proxy):
        # type: (MatchingTrackProxy) -> None
        super(MatchingTrackSoloState, self).__init__()
        self._track_proxy = track_proxy

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, MatchingTrackProxy):
            tracks = [self._track_proxy.base_track._track, self._track_proxy.audio_track._track]
            self._solo_listener.replace_subjects(tracks)

    @subject_slot_group("solo")
    @defer
    def _solo_listener(self, track):
        # type: (Live.Track.Track) -> None
        self._track_proxy.base_track.solo = track.solo
        self._track_proxy.audio_track.solo = track.solo
