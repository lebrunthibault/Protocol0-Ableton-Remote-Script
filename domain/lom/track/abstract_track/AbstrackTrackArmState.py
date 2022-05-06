import Live

from typing import Optional

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class AbstractTrackArmState(object):
    def __init__(self, live_track):
        # type: (Live.Track.Track) -> None
        self._live_track = live_track

    @property
    def is_armed(self):
        # type: () -> bool
        return False

    @is_armed.setter
    def is_armed(self, _):
        # type: (bool) -> None
        pass

    @property
    def is_partially_armed(self):
        # type: () -> bool
        return False

    def toggle(self):
        # type: () -> Optional[Sequence]
        if not SongFacade.selected_track().IS_ACTIVE:
            return None
        if self.is_armed:
            self.unarm()
            return None
        else:
            return self.arm()

    def arm(self):
        # type: () -> Optional[Sequence]
        if self.is_armed:
            return None
        if self._live_track.is_foldable:
            self._live_track.fold_state = 1

        return self.arm_track()

    def arm_track(self):
        # type: () -> Optional[Sequence]
        raise Protocol0Warning("Tried arming unarmable %s" % self)

    def unarm(self):
        # type: () -> None
        self.is_armed = False
