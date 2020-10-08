from ClyphX_Pro.clyphx_pro.user_actions._Clip import Clip
from ClyphX_Pro.clyphx_pro.user_actions._TrackName import TrackName
from ClyphX_Pro.clyphx_pro.user_actions._TrackType import TrackType
from ClyphX_Pro.clyphx_pro.user_actions._log import log_ableton


class Track:
    def __init__(self, track, index):
        # type: (_, int) -> None
        self.g_track = None
        self.track = track
        self.index = index
        self.song = None

        try:
            playing_clip_index_track = int(track.name)
            # handle wrong track name
            if not self.track.clip_slots[playing_clip_index_track - 1].has_clip:
                playing_clip_index_track = 0
        except ValueError:
            playing_clip_index_track = 0

        self.playing_clip_index = next(
            iter([i + 1 for (i, clip_slot) in enumerate(list(track.clip_slots)) if
                  clip_slot.has_clip and clip_slot.clip.is_playing]),
            playing_clip_index_track)

        self.type = (TrackType.group if self.is_group
                     else TrackType.clyphx if self.is_clyphx
        else TrackType.audio if self.is_audio
        else TrackType.midi if self.is_midi
        else TrackType.any
                     )

    @property
    def name(self):
        # type: () -> str
        return self.track.name

    @property
    def current_output_routing(self):
        # type: () -> str
        return self.track.current_output_routing

    @property
    def is_foldable(self):
        # type: () -> str
        return self.track.is_foldable

    @property
    def is_groupable(self):
        # type: () -> bool
        return self.is_group or \
               self.is_clyphx or \
               (self.index >= 3 and self.song.tracks[self.index - 2].name == TrackName.GROUP_CLYPHX_NAME) or \
               (self.index >= 4 and self.song.tracks[self.index - 3].name == TrackName.GROUP_CLYPHX_NAME)

    @property
    def is_group(self):
        # type: () -> bool
        return self.name in TrackName.GROUP_EXT_NAMES

    @property
    def is_clyphx(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_CLYPHX_NAME

    @property
    def is_audio(self):
        # type: () -> bool
        return self.track.has_audio_input

    @property
    def is_midi(self):
        # type: () -> bool
        return self.track.has_midi_input

    @property
    def is_playing(self):
        # type: () -> bool
        return self.playing_clip_index != 0

    @property
    def is_visible(self):
        # type: () -> bool
        return self.track.is_visible

    @property
    def is_top_visible(self):
        # type: () -> bool
        return self.is_visible and self.name != TrackName.GROUP_CLYPHX_NAME and not self.name.isnumeric()

    @property
    def playing_clip(self):
        # type: () -> Clip
        """ return clip and clip clyphx index """
        if self.playing_clip_index != 0:
            return Clip(self.track.clip_slots[self.playing_clip_index - 1].clip, self.playing_clip_index)
        else:
            return None

    @property
    def beat_count_before_clip_restart(self):
        # type: () -> int
        """ return clip and clip clyphx index """
        if not self.playing_clip:
            return 0
        log_ableton("playing_clip.playing_position : %f" % self.playing_clip.playing_position)
        return int(round(self.playing_clip.length - self.playing_clip.playing_position))

    @property
    def arm(self):
        # type: () -> bool
        return self.track.arm

    @property
    def can_be_armed(self):
        # type: () -> bool
        return self.track.can_be_armed

    @property
    def clip_slots(self):
        # type: () -> list
        return list(self.track.clip_slots)

    @property
    def scene_count(self):
        # type: () -> int
        return len(self.clip_slots)

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
