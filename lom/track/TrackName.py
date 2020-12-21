from typing import TYPE_CHECKING

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
        self.name = self.parts[0]  # type: str
        try:
            self.clip_slot_index = int(self.parts[1])
        except (ValueError, IndexError):
            self.clip_slot_index = 0
        try:
            self.preset_index = int(self.parts[2])
        except (ValueError, IndexError):
            self.preset_index = 0

    def set(self, clip_slot_index=None, preset_index=None):
        # type: (int) -> None
        clip_slot_index = clip_slot_index if clip_slot_index is not None else self.clip_slot_index
        if clip_slot_index < 0 or clip_slot_index > len(self.track.song.scenes) - 1:
            raise "invalid clip_slot_index for track %s" % self.name

        name = "{0} - {1}".format(self.name, clip_slot_index)

        if self.track.instrument:
            preset_index = preset_index if preset_index is not None else self.preset_index
            name += " - {0}".format(preset_index)

        self.track.name = name

    def get_track_name(cls, clip_slot_index, preset_index):
        pass
