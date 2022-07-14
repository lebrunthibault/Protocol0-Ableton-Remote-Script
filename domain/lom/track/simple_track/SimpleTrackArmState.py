import Live

from protocol0.domain.lom.track.abstract_track.AbstrackTrackArmState import AbstractTrackArmState


class SimpleTrackArmState(AbstractTrackArmState):
    def __init__(self, live_track):
        # type: (Live.Track.Track) -> None
        super(SimpleTrackArmState, self).__init__(live_track)
        self._live_track = live_track

    @property
    def is_armed(self):
        # type: () -> bool
        return self._live_track.can_be_armed and self._live_track.arm

    @is_armed.setter
    def is_armed(self, is_armed):
        # type: (bool) -> None
        if self._live_track.can_be_armed:
            self._live_track.arm = is_armed

    @property
    def is_armable(self):
        # type: () -> bool
        """Checks for disabled input routing"""
        if not self._live_track.can_be_armed:
            return True
        self.is_armed = True
        if self.is_armed:
            self.is_armed = False
            return True
        else:
            return False

    def arm_track(self):
        # type: () -> None
        if self.is_armed:
            return None
        if self._live_track.is_foldable:
            self._live_track.fold_state = not self._live_track.fold_state
        else:
            self._live_track.mute = False
            self.is_armed = True

        self.notify_observers()
