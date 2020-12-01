from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0 import Protocol0Component
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Song import Song


class AbstractObject(object):
    def __init__(self, song=None, *a, **k):
        from a_protocol_0 import Protocol0Component
        self.parent = Protocol0Component.SELF  # type: "Protocol0Component"
        self.song = song if song else self.parent.song  # short-circuiting parent.song for Song instantiation
        self.parent.defer(self.init_listeners)

    def init_listeners(self):
        # type: () -> None
        pass

    # todo : add a wrapper to postpone listeners if needed
