from typing import Any, TYPE_CHECKING

from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.Dependency import depends

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0 import Protocol0Component
from a_protocol_0.lom.Song import Song
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


class AbstractControlSurfaceComponent(ControlSurfaceComponent):
    @depends(parent=None, my_song=None)
    def __init__(self, parent=None, my_song=None, *a, **k):
        # type: (Protocol0Component, Song, Any, Any) -> None
        super(AbstractControlSurfaceComponent, self).__init__(*a, **k)
        self.parent = parent
        self.control_surface = parent.control_surface
        self.song = my_song

    @property
    def current_track(self):
        # type: () -> AbstractTrack
        return self.song.current_track

