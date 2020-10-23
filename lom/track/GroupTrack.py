from typing import Any

from ClyphX_Pro.clyphx_pro.user_actions.actions.BomeCommands import BomeCommands
from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName
from ClyphX_Pro.clyphx_pro.user_actions.actions.Actions import Actions
from ClyphX_Pro.clyphx_pro.user_actions.utils.log import log_ableton


class GroupTrack(AbstractTrack):
    def __init__(self, song, base_track):
        # type: ("Song", Any) -> None
        # getting our track object
        self.song = song
        track = song.get_track(base_track)
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
        self.clyphx.g_track = self.midi.g_track = self.audio.g_track = self

        super(GroupTrack, self).__init__(self.group.track, self.track_index_group)

    def action_arm(self):
        # type: () -> str
        action_list = Actions.restart_track(self.midi, self.audio)
        # stop audio to have live synth parameter edition while midi is playing
        action_list += Actions.stop_track(self.audio)
        # disable other clip colors
        action_list += "; {0}/clip(1) color {1}".format(self.clyphx.index, Colors.ARM)
        action_list += "; {0}/fold off".format(self.group.index)
        action_list += Actions.arm_g_track(self)
        action_list += "; push msg 'tracks {0} armed'".format(self.name)

        # activate the rev2 editor for this group track
        if self.is_prophet:
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

        # we delay the arming off of the audio track to have the audio playing until the end of the clip
        # keeps sync on for long clips
        # if not self.midi.is_playing or not self.audio.is_playing:
        #     action_list += "; waits {0}".format(self.beat_count_before_clip_restart - 1)

        if self.audio.is_playing:
            action_list += Actions.restart_track(self.midi, self.audio)
        elif self.midi.is_playing:
            action_list += Actions.restart_track(self.audio, self.midi)

        action_list += "; waits 2; {0}/arm off".format(self.audio.index)

        if direct_unarm:
            action_list += "; push msg 'tracks {0} unarmed'".format(self.name)

        return action_list

    def action_sel(self):
        # type: () -> str
        action_list = ""
        if self.song.selected_track == self.selectable_track:
            action_list += "; {0}/fold on; {0}/sel".format(self.group.index)
            return action_list

        action_list += "; {0}/fold off; {1}/sel".format(self.group.index, self.selectable_track.index)
        if self.is_prophet:
            action_list += BomeCommands.SHOW_AND_ACTIVATE_REV2_EDITOR
        else:
            action_list += BomeCommands.SELECT_FIRST_VST
        action_list += Actions.arm_g_track(self)

        return action_list

    def action_start_or_stop(self):
        # type: () -> str
        if self.audio.is_playing:
            return Actions.stop_track(self.audio)
        else:
            return Actions.restart_track(self.audio, self.midi)

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
    def is_group(self):
        # type: () -> bool
        return True

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
    def rec_clip_index(self):
        # type: () -> int
        return self.audio.rec_clip_index

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
    def beat_count_before_clip_restart(self):
        # type: () -> int
        if self.audio.beat_count_before_clip_restart:
            return self.audio.beat_count_before_clip_restart
        else:
            return self.midi.beat_count_before_clip_restart
