import traceback
from typing import TYPE_CHECKING, Any

from _Framework.SubjectSlot import subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
    # noinspection PyUnresolvedReferences
    from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


def button_action(is_scrollable=False, auto_arm=False, log_action=True):
    def wrap(func):
        @subject_slot("value")
        def decorate(self, *a, **k):
            # type: (AbstractControlSurfaceComponent, Any, Any) -> None
            value = a[0]
            if not value:
                return
            if is_scrollable:
                k = dict(k, go_next=value == 1)
            if log_action:
                self.parent.log("Executing " + func.__name__, debug=False)
            try:
                if auto_arm:
                    self.song.unfocus_all_tracks()
                    if not self.current_track.arm:
                        self.current_track.action_arm()
                func(self, **k)
            except Exception:
                self.parent.log(traceback.format_exc(), debug=False)
                return

        return decorate

    return wrap
