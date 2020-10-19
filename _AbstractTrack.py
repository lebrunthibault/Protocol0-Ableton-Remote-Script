from typing import Any
from abc import ABCMeta, abstractproperty


# noinspection PyDeprecation
class AbstractTrack:
    __metaclass__ = ABCMeta

    def __init__(self, song, track, index):
        # type: (Any, Any, int) -> None
        self.song = song
        self.track = track
        self.index = index
        self.g_track = None

    def __eq__(self, other):
        if isinstance(other, AbstractTrack):
            return self.track == other.track
        return False

    @abstractproperty
    def name(self):
        # type: () -> str
        pass
        # return self.track.name

    @abstractproperty
    def is_group(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_foldable(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_folded(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_playing(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_visible(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_top_visible(self):
        # type: () -> bool
        pass

    @abstractproperty
    def is_armed(self):
        # type: () -> bool
        pass

    @abstractproperty
    def scene_count(self):
        # type: () -> int
        pass

    @abstractproperty
    def first_empty_slot_index(self):
        # type: () -> int
        pass

    @abstractproperty
    def rec_clip_index(self):
        # type: () -> int
        pass
