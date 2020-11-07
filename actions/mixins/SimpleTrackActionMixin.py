from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.MiscUtils import get_beat_time
import Live

from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackActionMixin(object):
    def action_arm(self):
        # type: ("SimpleTrack") -> None
        self.arm = True

    # noinspection PyUnusedLocal
    def action_unarm(self, *args):
        # type: ("SimpleTrack", bool) -> None
        self.arm = False

    def action_sel(self):
        # type: ("SimpleTrack") -> str
        self.is_folded = not self.is_folded
        self.is_selected = True
        return self.instrument.action_show

    def action_switch_monitoring(self):
        # type: ("SimpleTrack") -> None
        self.has_monitor_in = not self.has_monitor_in

    def action_record_all(self):
        # type: ("SimpleTrack") -> None
        if self.can_be_armed and self.song.session_record_status == Live.Song.SessionRecordStatus.off:
            length = get_beat_time('%sb' % self.bar_count, self.song.song)
            self.clip_slots[self.next_empty_clip_slot.index].fire(record_length=length)

    def action_record_audio_only(self):
        # type: ("SimpleTrack") -> None
        self.action_record_all()

    def action_post_record(self):
        # type: ("SimpleTrack") -> None
        self.song.metronome = False
        if self.is_audio:
            self.playing_clip.clip.warp_mode = Live.Clip.WarpMode.complex

        self.playing_clip.name = "[] sel/name '{0}'".format(TrackName(self).get_track_name_for_clip_index())

    def stop(self):
        # type: ("SimpleTrack") -> None
        self.track.stop_all_clips()

    def action_restart(self):
        # type: ("SimpleTrack") -> None
        self.playing_clip.is_playing = True

    def action_undo(self):
        # type: ("SimpleTrack") -> None
        if self.is_recording:
            self.action_delete_current_clip()
        elif self.is_triggered:
            self.stop()
        else:
            self.song.undo()

    def action_delete_current_clip(self):
        # type: ("SimpleTrack") -> None
        self.song.metronome = False
        self.playing_clip.action_delete()
        self.name = TrackName(self).get_track_name_for_clip_index(self.previous_clip.index)
