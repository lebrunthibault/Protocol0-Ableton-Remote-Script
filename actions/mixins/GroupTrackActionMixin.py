import time

from typing import Optional, TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.actions.BomeCommands import BomeCommands
from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions.actions.Actions import Actions

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack


# noinspection PyTypeHints
class GroupTrackActionMixin(object):
    def action_arm(self, add_select_action=True):
        # type: ("GroupTrack", Optional[bool]) -> str
        # stop audio to have live synth parameter edition while midi is playing
        self.audio.set_monitor_in()
        # disable other clip colors
        action_list = "; {0}/clip(1) color {1}".format(self.clyphx.index, Colors.ARM)
        action_list += "; {0}/fold off".format(self.group.index)
        action_list += "; {0}/arm off; {1}/arm on; {2}/arm on".format(self.clyphx.index, self.midi.index,
                                                                      self.audio.index)
        # action_list += "; push msg 'tracks {0} armed'".format(self.name)

        # activate the rev2 editor for this group track
        if add_select_action and self.is_prophet_group_track:
            action_list += "; {0}/sel_ext; wait 10; {0}/sel".format(self.index)

        return action_list

    def action_unarm(self, direct_unarm=False):
        # type: ("GroupTrack", bool) -> str
        action_list = "; {0}/clip(1) color {1}; {2}/fold off".format(
            self.clyphx.index, self.color, self.group.index)

        action_list += "; {0}/arm {1}".format(self.clyphx.index, "on" if direct_unarm else "off")
        if self.audio.is_playing:
            action_list += Actions.set_audio_playing_color(self, Colors.PLAYING)

        action_list += "; {0}, {1}/arm off".format(self.midi.index, self.audio.index)
        self.audio.set_monitor_in(False)

        if direct_unarm:
            action_list += "; push msg 'tracks {0} unarmed'".format(self.name)

        return action_list

    def action_sel(self):
        # type: ("GroupTrack") -> str
        if self.song.selected_track == self.selectable_track:
            return "; {0}/fold on; {0}/sel".format(self.group.index)

        action_list = self.action_arm(False)
        action_list += "; {0}/fold off".format(self.group.index)
        action_list += self.selectable_track.action_sel()

        return action_list

    def action_record(self, bar_count):
        # type: ("GroupTrack", int) -> str
        action_list_rec = "; {0}/recfix {2} {3}; {1}/recfix {2} {3}; {0}/name '{4}'; {1}/name '{5}'".format(
            self.midi.index, self.audio.index, bar_count, self.rec_clip_index,
            self.midi.get_track_name_for_playing_clip_index(self.rec_clip_index),
            self.audio.get_track_name_for_playing_clip_index(self.rec_clip_index),
        )
        action_list = Actions.restart_and_record(self, action_list_rec)
        # when done, stop audio clip and metronome
        action_list += "; wait {0}; metro off;".format(self.song.delay_before_recording_end(bar_count))

        # rename timestamp clip to link clips
        timestamp = time.time()
        action_list += "; {0}/clip({1}) name {2}".format(self.midi.index, self.rec_clip_index, timestamp)
        action_list += "; {0}/clip({1}) name {2}; {0}/clip({1}) warpmode complex".format(self.audio.index,
                                                                                         self.rec_clip_index, timestamp)

        self.audio.set_monitor_in()

        return action_list

    def action_record_audio(self):
        # type: ("GroupTrack") -> str
        action_list = self.action_arm()
        action_list += Actions.add_scene_if_needed(self.audio)

        if not self.midi.is_playing:
            return action_list + self.audio.action_record_audio()

        action_list += Actions.delete_current_clip(self.audio) if self.is_recording else ""

        action_list_rec = "; {0}/recfix {1} {2}; {0}/name '{2}'".format(
            self.audio.index, self.rec_length_from_midi, self.rec_clip_index,
            self.audio.get_track_name_for_playing_clip_index(self.rec_clip_index)
        )
        action_list += Actions.restart_and_record(self, action_list_rec, False)
        # when done, stop audio clip
        action_list += "; wait {0}; {1}/clip({2}) name '{3}'; {1}/clip({2}) warpmode complex".format(
            self.delay_before_recording_end, self.audio.index, self.rec_clip_index, self.midi.playing_clip.name)
        action_list += Actions.set_audio_playing_color(self, Colors.PLAYING)

        return action_list

    def action_undo(self):
        # type: ("GroupTrack") -> str
        return self.audio.action_undo() + self.midi.action_undo()

    def action_restart(self):
        # type: ("GroupTrack") -> str
        return Actions.restart_track(self.midi) + Actions.restart_track(self.audio)

    @staticmethod
    def action_scroll_preset_or_sample(go_next):
        # type: (bool) -> str
        return str(go_next)
