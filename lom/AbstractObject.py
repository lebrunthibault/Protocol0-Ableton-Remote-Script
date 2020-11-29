from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from a_protocol_0.Protocol0Component import Protocol0Component


class AbstractObject(object):
    def __init__(self, *a, **k):
        self.init_listeners()

    def __ne__(self, other):
        return not self == other

    def init_listeners(self):
        pass

    @property
    def parent(self):
        # type: () -> "Protocol0Component"
        from a_protocol_0.Protocol0Component import Protocol0Component
        if hasattr(self, 'parent') and isinstance(self.parent, Protocol0Component):
            return self.parent
        from a_protocol_0.lom.Song import Song
        if hasattr(self, 'song') and isinstance(self.song, Song):
            return self.song.parent
        from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
        if hasattr(self, 'track') and isinstance(self.track, AbstractTrack):
            return self.track.parent

        raise Exception("couldn't get parent from AbstractObject")
