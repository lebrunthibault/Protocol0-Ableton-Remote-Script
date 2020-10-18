from typing import Any, Optional
from ClyphX_Pro.clyphx_pro.user_actions._Clip import Clip
from ClyphX_Pro.clyphx_pro.user_actions._TrackName import TrackName
from ClyphX_Pro.clyphx_pro.user_actions._TrackType import TrackType

class Track:
    def __init__(self, track, index):
        # type: (Any, int) -> None
        self.g_track = None
        self.track = track
        self.index = index
        self.song = None

        try:
            playing_clip_index_track = self.clips[int(self.name)]
        except (ValueError, KeyError):
            playing_clip_index_track = 0

        self.playing_clip_index = next(iter(self.playing_clips), playing_clip_index_track)

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
        # type: () -> bool
        return self.track.is_foldable

    @property
    def is_folded(self):
        # type: () -> bool
        return self.track.fold_state

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
        return bool(self.playing_clip)

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
        # type: () -> Optional[Clip]
        """ return clip and clip clyphx index """
        if self.playing_clip_index != 0:
            return self.clips[self.playing_clip_index]
        else:
            return None

    @property
    def clips(self):
        # type: () -> dict[int, Clip]
        """ return clip and clip clyphx index """
        return { index: Clip(clip_slot.clip, index + 1) for (index, clip_slot) in enumerate(self.clip_slots) if clip_slot.has_clip}

    @property
    def playing_clips(self):
        # type: () -> list[Clip]
        """ return clip and clip clyphx index """
        return [clip for clip in self.clips.values() if clip.is_playing]

    @property
    def beat_count_before_clip_restart(self):
        # type: () -> int
        """ return clip and clip clyphx index """
        if not self.playing_clip:
            return 0
        return int(round(self.playing_clip.length - self.playing_clip.playing_position))

    @property
    def is_armed(self):
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
        return self.first_empty_slot_index if self.has_empty_slot else self.scene_count + 1

    def get_last_clip_index_by_name(self, name):
        # type: (Track, str) -> Optional[Clip]
        """ get last clip with name on track """
        clips_matching_name = [clip for clip in self.clips.values() if clip.name == name]
        return clips_matching_name.pop().index if len(clips_matching_name) else None

    # @property
    # def linked_audio_playing_clip(self):
    #     # type: () -> Clip
    #     """ return clip and clip clyphx index """
    #     if not self.g_track.midi.playing:
    #         return None
    #     else:
    #         return list(self.clip_slots[]