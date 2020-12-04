from typing import Any, TYPE_CHECKING

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class AbstractControlSurfaceComponent(AbstractObject, ControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        AbstractObject.__init__(self, *a, **k)
        ControlSurfaceComponent.__init__(self, song=self.parent.protocol0_song, *a, **k)

    @property
    def selected_track(self):
        # type: () -> SimpleTrack
        return self.song.selected_track

    @property
    def current_track(self):
        # type: () -> AbstractTrack
        return self.song.current_track

