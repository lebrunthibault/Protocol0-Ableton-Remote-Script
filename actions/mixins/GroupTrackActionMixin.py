from typing import Optional, TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack


# noinspection PyTypeHints
class GroupTrackActionMixin(object):
    @property
    def action_arm(self):
        # type: ("GroupTrack", Optional[bool]) -> str
        # stop audio to have live synth parameter edition while midi is playing

        action_list = "; {0}/clip(1) color {1}".format(self.clyphx.index, Colors.ARM)
        action_list += "; {0}/fold off".format(self.group.index)
        action_list += "; {0}/arm off; {1}/arm on; {2}/arm on".format(self.clyphx.index, self.midi.index,
                                                                      self.audio.index)

        if self.song.current_action_name in ("sel_ext", "arm_ext"):
            action_list += self.audio.action_set_monitor_in()

        # activate the rev2 editor for this group track
        if self.is_prophet_group_track:
            action_list += "; {0}/sel_ext; wait 10; {0}/sel".format(self.index)

        return action_list

    def action_unarm(self, direct_unarm):
        # type: ("GroupTrack", bool) -> str
        action_list = "; {0}/clip(1) color {1}; {2}/fold off".format(
            self.clyphx.index, self.color, self.group.index)

        action_list += "; {0}/arm {1}".format(self.clyphx.index, "on" if direct_unarm else "off")
        if self.audio.is_playing:
            action_list += self.action_set_audio_playing_color(Colors.PLAYING)

        action_list += "; {0}, {1}/arm off".format(self.midi.index, self.audio.index)
        action_list += self.audio.action_set_monitor_in(False)

        return action_list

    @property
    def action_sel(self):
        # type: ("GroupTrack") -> str
        if self.song.selected_track == self.selectable_track:
            return "; {0}/fold on; {0}/sel".format(self.group.index)

        action_list = self.action_arm
        action_list += "; {0}/fold off".format(self.group.index)
        action_list += self.selectable_track.action_sel

        return action_list

    def action_record_all(self):
        # type: ("GroupTrack", int) -> str
        return self.audio.action_record_all() + self.midi.action_record_all()

    def action_record_audio_only(self):
        # type: ("GroupTrack", int) -> str
        if self.midi.is_playing:
            self.song.bar_count = self.rec_length_from_midi

        return self.audio.action_record_all()

    @property
    def action_rename_recording_clip(self):
        # type: ("GroupTrack") -> str
        action_list = self.midi.action_rename_recording_clip
        action_list += self.audio.action_rename_recording_clip
        # handle group track rename
        action_list += '; wait 1; {0}/name "{1}"'.format(self.group.index, self.group.name)

        return action_list

    @property
    def action_stop(self):
        # type: ("GroupTrack") -> str
        return self.midi.action_stop + self.audio.action_stop

    @property
    def action_undo(self):
        # type: ("GroupTrack") -> str
        return self.audio.action_undo + self.midi.action_undo

    def action_set_audio_playing_color(self, color):
        # type: ("GroupTrack", int) -> str
        return "; {0}/clip(2) color {1}".format(self.clyphx.index, color)
