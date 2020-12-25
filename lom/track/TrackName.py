from typing import TYPE_CHECKING, Optional

from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class TrackName(AbstractObject):
    def __init__(self, track, *a, **k):
        # type: (SimpleTrack) -> None
        super(TrackName, self).__init__(*a, **k)
        self.track = track
        self.parts = track._track.name.split(" - ")

    @property
    def name(self):
        # type: () -> str
        return self.parts[0]

    @name.setter
    def name(self, name):
        return self._set(name=name)

    @property
    def clip_slot_index(self):
        # type: () -> int
        try:
            return int(self.parts[1])
        except (ValueError, IndexError):
            return 0

    @clip_slot_index.setter
    def clip_slot_index(self, clip_slot_index):
        # type: () -> int
        return self._set(clip_slot_index=clip_slot_index)

    @property
    def preset_index(self):
        # type: () -> int
        try:
            return int(self.parts[2])
        except (ValueError, IndexError):
            return 0

    @preset_index.setter
    def preset_index(self, preset_index):
        return self._set(preset_index=preset_index)

    def _set(self, name=None, clip_slot_index=None, preset_index=None):
        # type: (Optional[str], Optional[int], Optional[int]) -> None
        clip_slot_index = clip_slot_index if clip_slot_index is not None else self.clip_slot_index
        if clip_slot_index < 0 or clip_slot_index > len(self.track.song.scenes) - 1:
            raise "invalid clip_slot_index for track %s" % self.name

        name = "{0} - {1}".format(name if name else self.name, clip_slot_index)

        if self.track.instrument:
            preset_index = preset_index if preset_index is not None else self.preset_index
            name += " - {0}".format(preset_index)

        self.track.name = name
