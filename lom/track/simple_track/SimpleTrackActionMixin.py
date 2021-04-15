from functools import partial

from typing import TYPE_CHECKING

from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import scroll_values

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackActionMixin(object):
    def arm_track(self):
        # type: (SimpleTrack) -> Sequence
        if self.is_foldable:
            self.is_folded = not self.is_folded
        else:
            self.mute = False
            self.is_armed = True

        if self.instrument and self.instrument.needs_exclusive_activation:
            return self.instrument.check_activated()

    def action_switch_monitoring(self):
        # type: (SimpleTrack) -> None
        self.has_monitor_in = not self.has_monitor_in

    def action_record_all(self):
        # type: (SimpleTrack, int) -> None
        """ finishes on end of recording """
        seq = Sequence()
        seq.add(self.clip_slots[self.next_empty_clip_slot_index].record)
        seq.add(self._post_record)
        return seq.done()

    def action_undo_track(self):
        # type: (SimpleTrack) -> None
        if self.is_recording:
            self.delete_current_clip()
        elif self.is_triggered:
            self.stop()
        else:
            self.song.undo()

    def create_clip(self, clip_slot_index=0, name=None, bar_count=1):
        # type: (SimpleTrack, int, str, int, callable, int) -> Sequence
        clip_slot = self.clip_slots[clip_slot_index]
        if clip_slot.has_clip:
            return

        seq = Sequence()
        seq.add(partial(clip_slot._clip_slot.create_clip,
                        self.parent.utilsManager.get_beat_time(bar_count)),
                complete_on=clip_slot._has_clip_listener)
        if name:
            seq.add(lambda: setattr(self.clip_slots[clip_slot_index].clip, "name", name), name="set clip name")

        return seq.done()

    def delete_current_clip(self):
        # type: (SimpleTrack) -> None
        self.song.metronome = False
        self.playable_clip.delete()

    def scroll_clips(self, go_next):
        # type: (SimpleTrack, bool) -> None
        selected_clip_slot = None  # type: ClipSlot
        self.parent.clyphxNavigationManager.show_clip_view()
        if not len(self.clips):  # scroll clip_slots when track is empty
            if self.song.highlighted_clip_slot and self.song.highlighted_clip_slot.index == 0 and not go_next:
                return self.parent.keyboardShortcutManager.up()
            selected_clip_slot = scroll_values(self.clip_slots, self.song.highlighted_clip_slot,
                                               go_next)  # type: ClipSlot
        else:
            if self.playable_clip == self.clips[0] and not go_next:
                return self.parent.keyboardShortcutManager.up()

            selected_clip = scroll_values(self.clips, self.playable_clip, go_next)  # type: Clip
            self.playable_clip.is_selected = False
            selected_clip.is_selected = True
            selected_clip_slot = selected_clip.clip_slot

        self.song.highlighted_clip_slot = selected_clip_slot
