from typing import Any, Optional, TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.actions.mixins.SimpleTrackActionMixin import SimpleTrackActionMixin
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrumentFactory import AbstractInstrumentFactory
from ClyphX_Pro.clyphx_pro.user_actions.lom.Clip import Clip
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack


class SimpleTrack(SimpleTrackActionMixin, AbstractTrack):
    SAMPLE_PATH = "C:/Users/thiba/Google Drive/music/software presets/Ableton User Library/Samples/Imported"

    def __init__(self, song, track, index):
        # type: (Any, Any, int) -> None
        self.g_track = None  # type: Optional["GroupTrack"]
        super(SimpleTrack, self).__init__(song, track, index)

    @property
    def index(self):
        return self._index

    @property
    def track(self):
        return self._track

    @property
    def instrument(self):
        # type: () -> AbstractInstrument
        return AbstractInstrumentFactory.create_from_simple_track(self)

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
        return self.name.is_group_track or \
               self.is_clyphx or \
               (self.index >= 3 and self.song.tracks[self.index - 2].name.is_clyphx) or \
               (self.index >= 4 and self.song.tracks[self.index - 3].name.is_clyphx)

    @property
    def is_nested_group_ex_track(self):
        # type: () -> bool
        return self.name.is_clyphx or \
               (self.index >= 3 and self.song.tracks[self.index - 2].name.is_clyphx) or \
               (self.index >= 4 and self.song.tracks[self.index - 3].name.is_clyphx)

    @property
    def is_clyphx(self):
        # type: () -> bool
        return self.name.is_clyphx

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
    def is_top_visible(self):
        # type: () -> bool
        return self.is_visible and not self.is_nested_group_ex_track

    @property
    def devices(self):
        # type: () -> list[Any]
        return self.track.devices

    @property
    def playing_clip(self):
        # type: () -> Optional[Clip]
        playing_clip_index = next(iter([clip.index for clip in self.clips.values() if clip.is_playing]),
                                  self.name.clip_index)
        try:
            return self.clips[playing_clip_index] if playing_clip_index != 0 else Clip(None, 0)
        except KeyError:
            return Clip(None, 0)

    @property
    def recording_clip(self):
        # type: () -> Optional[Clip]
        return next(iter([clip for clip in self.clips.values() if clip.is_recording]), None)

    @property
    def previous_clip(self):
        try:
            clip_index = list(self.clips.values()).index(self.playing_clip)
            if clip_index != 0:
                return list(self.clips.values())[clip_index - 1]
            return Clip(None, 0)
        except ValueError:
            return Clip(None, 0)

    @property
    def clips(self):
        # type: () -> dict[int, Clip]
        """ return clip and clip clyphx index """
        return {index + 1: Clip(clip_slot.clip, index + 1) for (index, clip_slot) in enumerate(self.clip_slots) if
                clip_slot.has_clip}

    @property
    def is_armed(self):
        # type: () -> bool
        return self.can_be_armed and self.track.arm

    @property
    def can_be_armed(self):
        # type: () -> bool
        return self.track.can_be_armed

    @property
    def has_monitor_in(self):
        # type: () -> bool
        return self.track.current_monitoring_state == 0

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
                  clip_slot.clip is None]), None)

    @property
    def has_empty_slot(self):
        # type: () -> bool
        return self.first_empty_slot_index is not None

    @property
    def rec_clip_index(self):
        # type: () -> int
        return self.first_empty_slot_index if self.has_empty_slot else self.scene_count + 1

    @property
    def record_track(self):
        # type: () -> SimpleTrack
        return self

    @property
    def preset_index(self):
        # type: () -> int
        return self.name.preset_index
