import traceback
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
    # noinspection PyUnresolvedReferences
    from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


def button_action(auto_arm=False, log_action=True):
    def wrap(func):
        def decorate(self, *a, **k):
            # type: (AbstractControlSurfaceComponent, Any, Any) -> None
            if log_action:
                self.parent.log_info("Executing " + func.__name__)
            try:
                if auto_arm:
                    self.song.unfocus_all_tracks()
                    if not self.current_track.arm:
                        self.current_track.action_arm()
                func(self, **k)
            except Exception:
                self.parent.log_info(traceback.format_exc())
                return

        return decorate

    return wrap
