from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.MiscUtils import get_beat_time
import Live

from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackActionMixin(object):
    def action_arm_track(self):
        # type: ("SimpleTrack") -> None
        self.arm = True

    def action_unarm(self):
        # type: ("SimpleTrack", bool) -> None
        self.arm = False

    def action_sel_track(self):
        # type: ("SimpleTrack") -> None
        self.is_selected = True
        if self.is_foldable:
            self.is_folded = not self.is_folded
        else:
            self.instrument.action_show()

    def switch_monitoring(self):
        # type: ("SimpleTrack") -> None
        self.has_monitor_in = not self.has_monitor_in

    def action_scroll_devices(self):
        # type: ("AbstractTrack") -> None
        pass

    def action_record_all(self):
        # type: ("SimpleTrack") -> None
        if self.can_be_armed and self.song.session_record_status == Live.Song.SessionRecordStatus.off:
            length = get_beat_time('%sb' % self.bar_count, self.song.song)
            self.clip_slots[self.next_empty_clip_slot.index].fire(record_length=length)

    def action_record_audio_only(self):
        # type: ("SimpleTrack") -> None
        self.action_record_all()

    def stop(self):
        # type: ("SimpleTrack") -> None
        self.track.stop_all_clips()

    def restart(self):
        # type: ("SimpleTrack") -> None
        if self.playable_clip:
            self.playable_clip.is_playing = True

    def action_undo_track(self):
        # type: ("SimpleTrack") -> None
        if self.is_recording:
            self.delete_current_clip()
        elif self.is_triggered:
            self.stop()
        else:
            self.song.undo()

    def delete_current_clip(self):
        # type: ("SimpleTrack") -> None
        self.song.metronome = False
        self.playable_clip.delete()
