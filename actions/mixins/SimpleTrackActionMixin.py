from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.utils.log import log_ableton
from ClyphX_Pro.clyphx_pro.MiscUtils import get_beat_time

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack

# noinspection PyTypeHints
class SimpleTrackActionMixin(object):
    def action_arm(self):
        # type: ("SimpleTrack") -> None
        self.arm = True

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
        # noinspection PyAttributeOutsideInit
        self.has_monitor_in = not self.has_monitor_in

    def action_record_all(self):
        # type: ("SimpleTrack") -> None
        if self.can_be_armed and self.song._song.session_record_status == Live.Song.SessionRecordStatus.off:
            length = get_beat_time('%sb' % self.bar_count, self.song, is_legacy_bar=True)
            self.clip_slots[self.rec_clip_index].fire(record_length=length)

    def action_record_audio_only(self):
        # type: ("SimpleTrack") -> None
        self.action_record_all()

    @property
    def action_rename_recording_clip(self):
        # type: ("SimpleTrack") -> str
        track_name = self.name.get_track_name_for_playing_clip_index(self.rec_clip_index)
        return "; {0}/clip({1}) name \"{2}\"".format(self.index, self.rec_clip_index, "[] sel/name '{0}'".format(track_name))

    def stop_all_clips(self):
        # type: ("SimpleTrack") -> None
        self.track.stop_all_clips()

    def action_restart(self):
        # type: ("SimpleTrack") -> None
        log_ableton(self.playing_clip.index)
        self.playing_clip.is_playing = True

    @property
    def action_undo(self):
        # type: ("SimpleTrack") -> str
        if not self.is_playing:
            self.song.undo()
        if self.is_recording:
            return self.action_delete_current_clip
        return ""

    def action_add_scene_if_needed(self):
        # type: ("SimpleTrack") -> None
        if not self.has_empty_slot:
            self.song.create_scene()

    @property
    def action_delete_current_clip(self):
        # type: ("SimpleTrack") -> str
        if not self.is_playing:
            return ""

        self.song.metronome = False
        action_list = ";{0}/clip({1}) del".format(self.index, self.playing_clip.index)
        if self.is_recording:
            action_list = "; GQ 1; {0}/stop; wait 2; {1}; GQ {2}".format(self.index, action_list,
                                                                         self.song.clip_trigger_quantization)

        previous_clip_index = self.previous_clip.index if self.previous_clip else 0
        action_list += "; {0}/name '{1}'".format(self.index,
                                                 self.name.get_track_name_for_playing_clip_index(previous_clip_index))

        return action_list
