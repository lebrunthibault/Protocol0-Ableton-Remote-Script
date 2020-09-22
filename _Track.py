from ClyphX_Pro.clyphx_pro.user_actions._Clip import Clip


class Track:
    def __init__(self, track, index):
        self.track = track
        self.index = index

        try:
            self.playing_clip_index = int(track.name)
        except ValueError:
            self.playing_clip_index = 0

    @property
    def name(self):
        # type: () -> str
        return self.track.name

    @property
    def is_playing(self):
        # type: () -> bool
        return self.playing_clip_index != 0

    @property
    def playing_clip(self):
        # type: () -> Clip
        """ return clip and clip clyphx index """
        if self.playing_clip_index != 0:
            return Clip(self.track.clip_slots[self.playing_clip_index - 1].clip, self.playing_clip_index)
        else:
            return None

    @property
    def arm(self):
        # type: () -> bool
        return self.track.arm

    @property
    def scene_count(self):
        # type: () -> int
        return len(list(self.track.clip_slots))

    @property
    def first_empty_slot_index(self):
        # type: () -> int
        """ counting in live index """
        return next(
            iter([i + 1 for i, clip_slot in enumerate(list(self.track.clip_slots)) if
                  clip_slot.clip is None and i not in (0, 1, 2)]), None)

    @property
    def has_empty_slot(self):
        # type: () -> bool
        return self.first_empty_slot_index is not None

    @property
    def rec_clip_index(self):
        # type: () -> int
        index = self.first_empty_slot_index

        return index if index else self.scene_count + 1
