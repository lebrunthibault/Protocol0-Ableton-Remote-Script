from typing import TYPE_CHECKING

from a_protocol_0.lom.Clip import Clip
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.utils.utils import get_beat_time, scroll_values

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackActionMixin(object):
    def action_arm_track(self):
        # type: (SimpleTrack) -> None
        self.mute = False
        self.arm = True

    def action_switch_monitoring(self):
        # type: (SimpleTrack) -> None
        self.has_monitor_in = not self.has_monitor_in

    def action_record_all(self, clip_slot_index=None):
        # type: (SimpleTrack, int) -> None
        clip_slot_index = clip_slot_index if clip_slot_index else self._next_empty_clip_slot_index
        length = get_beat_time('%sb' % self.bar_count, self.song._song)
        self.parent.show_message("Starting recording of %d bars" % self.bar_count)
        self.clip_slots[clip_slot_index].fire(record_length=length)

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
        if not len(self.clips):
            return

        selected_clip = scroll_values(self.clips, self.playable_clip, go_next)  # type: Clip
        self.parent.log_debug("clip.index %d" % selected_clip.index)
        for clip in self.clips:
            clip.color = self.base_color
            clip.is_selected = False
        selected_clip.is_selected = True
        selected_clip.color = Colors.SELECTED
