import time

from typing import Any, Optional

from ClyphX_Pro.clyphx_pro.user_actions.actions.BomeCommands import BomeCommands
from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName
from ClyphX_Pro.clyphx_pro.user_actions.actions.Actions import Actions


class GroupTrack(AbstractTrack):
    def __init__(self, song, base_track):
        # type: ("Song", Any) -> None
        # getting our track object
        track = song.get_track(base_track)
        self.song = song
        self.track_index_group = track.index - 1

        # check if we clicked on group track instead of clyphx track
        if track.is_clyphx:
            self.track_index_group -= 1

        if track.index >= 3 and song.tracks[track.index - 2].name == TrackName.GROUP_CLYPHX_NAME:
            self.track_index_group -= 2
        if track.index >= 4 and song.tracks[track.index - 3].name == TrackName.GROUP_CLYPHX_NAME:
            self.track_index_group -= 3

        if self.track_index_group < 0 or self.track_index_group > len(song.tracks) - 2:
            raise Exception(
                "tried to instantiate group track with base_track {0} and found track index {1}".format(base_track,
                                                                                                        self.track_index_group))
        super(GroupTrack, self).__init__(song, self.group.track, self.track_index_group)

        self.clyphx.g_track = self.midi.g_track = self.audio.g_track = self


    def action_arm(self, add_select_action=True):
        # type: (Optional[bool]) -> str
        # stop audio to have live synth parameter edition while midi is playing
        self.audio.set_monitor_in()
        # disable other clip colors
        action_list = "; {0}/clip(1) color {1}".format(self.clyphx.index, Colors.ARM)
        action_list += "; {0}/fold off".format(self.group.index)
        action_list += "; {0}/arm off; {1}/arm on; {2}/arm on".format(self.clyphx.index, self.midi.index,
                                                              self.audio.index)
        # action_list += "; push msg 'tracks {0} armed'".format(self.name)

        # activate the rev2 editor for this group track
        if add_select_action and self.is_prophet:
            action_list += "; {0}/sel_ext; wait 10; {0}/sel".format(self.index)

        return action_list

    def action_unarm(self, direct_unarm=False):
        # type: (bool) -> str
        action_list = "{0}/clip(1) color {1}; {2}/fold off".format(
            self.clyphx.index, self.color, self.group.index)

        if direct_unarm:
            action_list += "; {0}/arm on".format(self.clyphx.index)
        if self.audio.is_playing:
            action_list += Actions.set_audio_playing_color(self, Colors.PLAYING)

        action_list += "; {0}, {1}/arm off".format(self.midi.index, self.audio.index)
        self.audio.set_monitor_in(False)

        if direct_unarm:
            action_list += "; push msg 'tracks {0} unarmed'".format(self.name)

        return action_list

    def action_sel(self):
        # type: () -> str
        if self.song.selected_track == self.selectable_track:
            return "; {0}/fold on; {0}/sel".format(self.group.index)

        action_list = self.action_arm(False)
        action_list += "; {0}/fold off; {1}/sel".format(self.group.index, self.selectable_track.index)
        action_list += self.action_show()

        return action_list

    def action_show(self):
        # type: () -> str
        if self.is_prophet:
            return BomeCommands.SHOW_AND_ACTIVATE_REV2_EDITOR
        else:
            return BomeCommands.SELECT_FIRST_VST

    def action_record(self, bar_count):
        # type: (int) -> str
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
        action_list += "; {0}/clip({1}) name {2}".format(self.midi.index, self, timestamp)
        action_list += "; {0}/clip({1}) name {2}; {0}/clip({1}) warpmode complex".format(self.audio.index,
                                                                                         self, timestamp)

        self.audio.set_monitor_in()

        return action_list

    def action_record_audio(self):
        # type: () -> str
        action_list = self.action_arm()
        action_list += Actions.add_scene_if_needed(self.audio)

        if not self.midi.is_playing:
            return action_list + self.audio.action_record_audio()

        action_list += Actions.restart_track(self.midi)
        action_list_rec = "; {0}/recfix {1} {2}; {0}/name '{2}'".format(
            self.audio.index, int(round((self.midi.playing_clip.length + 1) / 4)),
            self.audio.get_track_name_for_playing_clip_index(self.rec_clip_index)
        )
        action_list += Actions.restart_and_record(self, action_list_rec, False)
        # when done, stop audio clip
        delay = int(round((600 / self.song().tempo) * (int(self.midi.playing_clip.length) + 6)))
        action_list += "; wait {0}; {1}/clip({2}) name '{3}'; {1}/clip({2}) warpmode complex".format(
            delay, self.audio.index, self.rec_clip_index, self.midi.playing_clip.name)
        action_list += Actions.set_audio_playing_color(self, Colors.PLAYING)

        return action_list

    def action_undo(self):
        # type: () -> str
        return Actions.delete_current_clip(self.audio) + Actions.delete_current_clip(self.midi)

    def action_restart(self):
        # type: () -> str
        return Actions.restart_track(self.midi) + Actions.restart_track(self.audio)
    @property
    def index(self):
        # type: () -> int
        return self.group.index

    @property
    def track(self):
        # type: () -> int
        return self.group.track

    @property
    def scene_count(self):
        return self.audio.scene_count

    @property
    def first_empty_slot_index(self):
        return self.audio.first_empty_slot_index

    @property
    def name(self):
        # type: () -> str
        return self.group.name

    @property
    def is_foldable(self):
        # type: () -> bool
        return True

    @property
    def is_folded(self):
        # type: () -> bool
        return self.group.track.is_folded

    @property
    def is_prophet(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_PROPHET_NAME

    @property
    def is_minitaur(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_MINITAUR_NAME

    @property
    def selectable_track(self):
        # type: () -> SimpleTrack
        return self.midi if self.is_prophet else self.audio

    @property
    def is_visible(self):
        # type: () -> bool
        return True

    @property
    def is_top_visible(self):
        # type: () -> bool
        return True

    @property
    def has_empty_slot(self):
        # type: () -> int
        return self.audio.has_empty_slot

    @property
    def group(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group]

    @property
    def clyphx(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 1]

    @property
    def midi(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 2]

    @property
    def audio(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 3]

    @property
    def is_armed(self):
        # type: () -> bool
        return self.midi.is_armed and self.audio.is_armed

    @property
    def any_armed(self):
        # type: () -> bool
        return self.clyphx.is_armed or self.midi.is_armed or self.audio.is_armed

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi.is_playing or self.audio.is_playing

    @property
    def color(self):
        # type: () -> str
        if "Prophet" in self.group.name:
            return Colors.PROPHET
        elif "BS" in self.group.name:
            return Colors.BASS_STATION
        return Colors.DISABLED

    @property
    def rec_clip_index(self):
        # type: () -> int
        return self.audio.rec_clip_index

    @property
    def record_track(self):
        # type: () -> SimpleTrack
        return self.audio