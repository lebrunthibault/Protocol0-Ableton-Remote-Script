from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0 import Protocol0Component
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.Song import Song


class AbstractObject(object):
    def __init__(self, *a, **k):
        from a_protocol_0 import Protocol0Component
        self.parent = Protocol0Component.SELF
        self.parent.wait(1, self.init_listeners)

    def __ne__(self, other):
        return not self == other

    @property
    def song(self):
        # type: () -> "Song"
        return self.parent.my_song()

    def init_listeners(self):
        # type: () -> None
        pass

    # todo : add a wrapper to postpone listeners if needed
