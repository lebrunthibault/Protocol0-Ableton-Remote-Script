from typing import Any, Optional

from ClyphX_Pro.clyphx_pro.user_actions.actions.Actions import Actions
from ClyphX_Pro.clyphx_pro.user_actions.lom.Clip import Clip
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackType import TrackType


class SimpleTrack(AbstractTrack):
    def __init__(self, song, track, index):
        # type: (Any, Any, int) -> None
        self.g_track = None
        self.song = song

        super(SimpleTrack, self).__init__(track, index)

    def action_arm(self):
        # type: () -> str
        return "{0}/arm on".format(self.index) if self.can_be_armed else ""

    def action_unarm(self, _):
        # type: (Optional[bool]) -> str
        return "{0}/arm off".format(self.index) if self.can_be_armed else ""

    def action_sel(self):
        # type: () -> str
        if not self.is_foldable:
            return ""
        return "{0}/fold {1}".format(self.index, "off" if self.is_folded else "on")

    def action_start_or_stop(self):
        # type: () -> str
        if self.is_playing:
            return Actions.stop_track(self)
        else:
            return Actions.restart_track(self)

    def action_record(self):
        # type: () -> str
        return ""

    def action_undo(self):
        # type: () -> str
        return Actions.delete_current_clip(self)

    def action_restart(self):
        # type: () -> str
        return Actions.restart_track(self)

    @property
    def index(self):
        return self._index

    @property
    def track(self):
        return self._track

    @property
    def type(self):
        return (TrackType.group if self.is_group_track_group
                else TrackType.clyphx if self.is_clyphx
        else TrackType.audio if self.is_audio
        else TrackType.midi if self.is_midi
        else TrackType.any
                )

    @property
    def name(self):
        return self.track.name

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
        return self.is_group_track_group or \
               self.is_clyphx or \
               (self.index >= 3 and self.song.tracks[self.index - 2].name == TrackName.GROUP_CLYPHX_NAME) or \
               (self.index >= 4 and self.song.tracks[self.index - 3].name == TrackName.GROUP_CLYPHX_NAME)

    @property
    def is_simple(self):
        # type: () -> bool
        return not self.is_groupable

    @property
    def is_group_track_group(self):
        # type: () -> bool
        return self.name in TrackName.GROUP_EXT_NAMES

    @property
    def is_nested_group_ex_track(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_CLYPHX_NAME or self.name.isnumeric()

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
    def is_simpler(self):
        # type: () -> bool
        return self.devices[0].class_name == "OriginalSimpler"

    @property
    def is_playing(self):
        # type: () -> bool
        return bool(self.playing_clip) and self.playing_clip.is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return bool(self.recording_clip)

    @property
    def is_visible(self):
        # type: () -> bool
        return self.track.is_visible

    @property
    def devices(self):
        # type: () -> list[Any]
        return self.track.devices

    @property
    def is_top_visible(self):
        # type: () -> bool
        return self.is_visible and not self.is_nested_group_ex_track

    @property
    def playing_clip(self):
        # type: () -> Optional[Clip]
        playing_clip_index = next(iter([clip.index for clip in self.playing_clips]), self.playing_clip_index_from_track_name)
        return self.clips[playing_clip_index] if playing_clip_index != 0 else Clip(None, 0)

    @property
    def recording_clip(self):
        # type: () -> Optional[Clip]
        return next(iter([clip for clip in self.clips.values() if clip.is_recording]), None)

    def get_track_name_for_playing_clip_index(self, playing_clip_index = None):
        # type: (Optional[int]) -> str
        return "{0} - {1}".format(self.name.split(" - ")[0], playing_clip_index if playing_clip_index else self.playing_clip.index)

    @property
    def playing_clip_index_from_track_name(self):
        # type: () -> int
        try:
            name = self.name.split(" - ")
            return 0 if len(name) == 1 else int(name[1])
        except ValueError:
            return 0

    @property
    def clips(self):
        # type: () -> dict[int, Clip]
        """ return clip and clip clyphx index """
        return {index + 1: Clip(clip_slot.clip, index + 1) for (index, clip_slot) in enumerate(self.clip_slots) if
                clip_slot.has_clip}

    @property
    def playing_clips(self):
        # type: () -> list[Clip]
        """ return clip and clip clyphx index """
        return [clip for clip in self.clips.values() if clip.is_playing]

    @property
    def beat_count_before_clip_restart(self):
        # type: () -> int
        """ return clip and clip clyphx index """
        if not self.is_playing:
            return 0
        return int(round(self.playing_clip.length - self.playing_clip.playing_position))

    @property
    def is_armed(self):
        # type: () -> bool
        return self.can_be_armed and self.track.arm

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
        # type: (str) -> Optional[Clip]
        """ get last clip with name on track """
        clips_matching_name = [clip for clip in self.clips.values() if clip.name == name]
        return clips_matching_name.pop() if len(clips_matching_name) else None

    # @property
    # def linked_audio_playing_clip(self):
    #     # type: () -> Clip
    #     """ return clip and clip clyphx index """
    #     if not self.g_track.midi.playing:
    #         return None
    #     else:
    #         return list(self.clip_slots[]
