from typing import Optional

from protocol0.domain.lom.track.abstract_track.AbstractMatchingTrack import AbstractMatchingTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.shared.sequence.Sequence import Sequence


class SimpleMidiMatchingTrack(AbstractMatchingTrack):
    def connect_main_track(self):
        # type: () -> Optional[Sequence]
        super(SimpleMidiMatchingTrack, self).connect_main_track()
        seq = Sequence()

        # select the first midi clip
        seq.add(ApplicationViewFacade.show_clip)
        if len(self._base_track.clips) != 0:
            seq.defer()
            seq.add(self._base_track.clips[0].show_notes)

        return seq.done()
