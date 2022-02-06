from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from protocol0.shared.AccessContainer import AccessContainer
from protocol0.shared.AccessSong import AccessSong


class AbstractControlSurfaceComponent(AccessContainer, AccessSong, ControlSurfaceComponent):
    pass
