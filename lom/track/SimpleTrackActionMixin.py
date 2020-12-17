from typing import TYPE_CHECKING

from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.ClipSlot import ClipSlot
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.utils.utils import scroll_values

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackActionMixin(object):
    def action_arm_track(self):
        # type: (SimpleTrack) -> None
        if self.is_foldable:
            self.is_folded = not self.is_folded
        else:
            self.mute = False
            self.arm = True

        if len(self.all_devices):
            self.song.select_device(self.all_devices[0])

    def action_switch_monitoring(self):
        # type: (SimpleTrack) -> None
        self.has_monitor_in = not self.has_monitor_in

    def action_record_all(self, clip_slot_index=None):
        # type: (SimpleTrack, int) -> None
        clip_slot_index = clip_slot_index if clip_slot_index else self._next_empty_clip_slot_index
        self.parent.show_message("Starting recording of %d bars" % self.bar_count)
        self.clip_slots[clip_slot_index].fire(record_length=self.parent.utils.get_beat_time(self.bar_count))

    def restart(self):
        # type: (SimpleTrack) -> None
        if self.is_foldable:
            [sub_track.restart() for sub_track in self.sub_tracks]
        elif self.playable_clip:
            self.playable_clip.is_playing = True

    def action_undo_track(self):
        # type: (SimpleTrack) -> None
        if self.is_recording:
            self.delete_current_clip()
        elif self.is_triggered:
            self.stop()
        else:
            self.song.undo()

    def delete_current_clip(self):
        # type: (SimpleTrack) -> None
        self.song.metronome = False
        self.playable_clip.delete()

    def scroll_clips(self, go_next):
        # type: (SimpleTrack, bool) -> None
        selected_clip_slot = None  # type: ClipSlot
        self.parent.clyphxNavigationManager.focus_main()
        if not len(self.clips):  # scroll clip_slots when track is empty
            if self.song.highlighted_clip_slot and self.song.highlighted_clip_slot.index == 0 and not go_next:
                return self.parent.keyboardShortcutManager.up()
            selected_clip_slot = scroll_values(self.clip_slots, self.song.highlighted_clip_slot, go_next)  # type: ClipSlot
        else:
            if self.playable_clip == self.clips[0] and not go_next:
                return self.parent.keyboardShortcutManager.up()
            selected_clip = scroll_values(self.clips, self.playable_clip, go_next)  # type: Clip
            for clip in self.clips:
                clip.color = self.base_color
                clip.is_selected = False
            selected_clip.is_selected = True
            selected_clip.color = Colors.SELECTED
            selected_clip_slot = selected_clip.clip_slot

        self.song.highlighted_clip_slot = selected_clip_slot
