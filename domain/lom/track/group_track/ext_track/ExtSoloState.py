import time

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager, subject_slot_group

from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.utils.timing import defer


class ExtSoloState(SlotManager):
    def __init__(self, base_track):
        # type: (SimpleAudioTrack) -> None
        super(ExtSoloState, self).__init__()
        self._base_track = base_track

        # this is necessary to monitor the group track solo state
        self._un_soloed_at = time.time()  # type: float

        self._solo_listener.subject = self._base_track._track

    def update(self):
        # type: () -> None
        self._sub_track_solo_listener.replace_subjects(
            [sub_track._track for sub_track in self._base_track.sub_tracks]
        )

    @property
    def solo(self):
        # type: () -> bool
        return self._base_track.solo

    @solo.setter
    def solo(self, solo):
        # type: (bool) -> None
        self._base_track.solo = solo

    @subject_slot("solo")
    def _solo_listener(self):
        # type: () -> None
        """We want to solo only the base track"""
        if not self.solo:
            self._un_soloed_at = time.time()

    @subject_slot_group("solo")
    @defer
    def _sub_track_solo_listener(self, track):
        # type: (Live.Track.Track) -> None
        """We want to solo only the base track"""
        if not track.solo:
            return

        track.solo = False  # noqa

        if self.solo:
            self.solo = False
        else:
            # Case : when the group track is soloed
            # and we want to un_solo it by toggling the solo state on the sub track
            # the group track is going to be un_soloed.
            # we need to check if it was un_soloed very recently meaning we should leave it like this
            # or not meaning we should solo it
            duration_since_last_un_solo = time.time() - self._un_soloed_at
            self.solo = duration_since_last_un_solo > 0.3
