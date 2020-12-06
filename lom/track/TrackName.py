from typing import TYPE_CHECKING, Optional, Any

from a_protocol_0.lom.AbstractObject import AbstractObject

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class TrackName(AbstractObject):
    def __init__(self, track, *a, **k):
        # type: (SimpleTrack, Any, Any) -> None
        super(TrackName, self).__init__(*a, **k)
        self.track = track
        self.parts = track.name.split(" - ")
        self.name = self.parts[0]  # type: str
        try:
            self.clip_slot_index = int(self.parts[1])
        except (ValueError, IndexError):
            self.clip_slot_index = 0
        try:
            self.preset_index = int(self.parts[2])
        except (ValueError, IndexError):
            self.preset_index = -1

    @property
    def has_instrument_preset(self):
        return len(self.parts) >= 3

    def get_track_name_for_clip_index(self, clip_index=None):
        # type: (Optional[int]) -> str
        clip_index = clip_index or self.track.playable_clip.index

        if clip_index < 0 or clip_index > len(self.track.song.scenes) - 1:
            return self.name

        name = "{0} - {1}".format(self.name,
                                  clip_index if clip_index is not None else self.track.playable_clip.index)

        if self.has_instrument_preset:
            name += " - {0}".format(self.preset_index)

        return name

    def get_track_name_for_preset_index(self, preset_index):
        # type: (int) -> str
        return "{0} - {1} - {2}".format(self.name, self.clip_slot_index, preset_index)
