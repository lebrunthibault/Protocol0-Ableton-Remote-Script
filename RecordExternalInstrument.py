import time

from ClyphX_Pro.clyphx_pro.user_actions._Actions import Actions
from ClyphX_Pro.clyphx_pro.user_actions._BomeCommands import BomeCommands
from ClyphX_Pro.clyphx_pro.user_actions._Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions._AbstractTrack import Track
from ClyphX_Pro.clyphx_pro.user_actions._utils import for_all_methods, init_song
from ClyphX_Pro.clyphx_pro.user_actions._AbstractUserAction import AbstractUserAction


@for_all_methods(init_song)
class RecordExternalInstrument(AbstractUserAction):
    """ Utility commands to record fixed length midi and audio on separate tracks """

    def create_actions(self):
        self.add_global_action('next_ext', self.next_ext)
        self.add_track_action('arm_ext', self.arm_ext)
        self.add_track_action('unarm_ext', self.unarm_ext)
        self.add_track_action('sel_ext', self.sel_ext)
        self.add_track_action('stop_audio_ext', self.stop_audio_ext)
        self.add_track_action('record_ext', self.record_ext)
        self.add_track_action('record_ext_audio', self.record_ext_audio)
        self.add_track_action('undo_ext', self.undo_ext)
        self.add_track_action('restart_ext', self.restart_ext)

    def next_ext(self, _, go_next="1"):
        """ arm or unarm both midi and audio track """
        go_next = bool(go_next)
        selected_track_index = self.song().selected_track.index if self.song().selected_track else 0
        action_list = "{0}/sel".format(self.get_next_track_by_index(selected_track_index, go_next).index)
        self.exec_action(action_list, None, "next_ext")

    def arm_ext(self, action_def, restart_clips=""):
        """ arm or unarm both midi and audio track """
        self.song().restart_clips = bool(restart_clips)
        g_track = self.get_group_track(action_def)

        if g_track.is_armed:
            return self.unarm_ext(action_def, "{0} {1}".format(restart_clips, "1"))

        if isinstance(g_track, Track):
            return self.exec_action("{0}/arm on".format(g_track.index), None, "arm_ext")

        action_list = "; setplay on" if g_track.is_playing and self.song().restart_clips else ""
        action_list += Actions.restart_track_on_group_press(g_track.midi, g_track.audio)
        # stop audio to have live synth parameter edition while midi is playing
        action_list += Actions.stop_track(g_track.audio, True)
        # disable other clip colors
        action_list += "; {0}/clip(1) color {1}".format(g_track.clyphx.index, Colors.ARM)
        action_list += "; {0}/fold off".format(g_track.group.index)
        action_list += Actions.arm_g_track(g_track)
        action_list += "; push msg 'tracks {0} armed'".format(g_track.name)

        # activate the rev2 editor for this group track
        if g_track.is_prophet:
            action_list += "; {0}/sel_ext; wait 10; {0}/sel".format(g_track.index)

        self.exec_action(action_list, g_track, "arm_ext")

    def unarm_ext(self, action_def, args=""):
        """ unarming group track """
        args = args.split(" ")
        self.song().restart_clips = bool(args[0])
        direct_unarm = len(args) > 1 and bool(args[1])
        g_track = self.get_group_track(action_def)

        if isinstance(g_track, Track):
            return self.exec_action("{0}/arm off".format(g_track.index), None, "arm_ext")

        action_list = "{0}/clip(1) color {1}; {2}/fold off".format(
            g_track.clyphx.index, g_track.color, g_track.group.index)

        if direct_unarm:
            action_list += "; {0}/arm on".format(g_track.clyphx.index)
        if g_track.audio.is_playing:
            action_list += Actions.set_audio_playing_color(g_track, Colors.PLAYING)

        action_list += "; {0}, {1}/arm off".format(g_track.midi.index, g_track.audio.index)

        # we delay the arming off of the audio track to have the audio playing until the end of the clip
        # keeps sync on for long clips
        # if not g_track.midi.is_playing or not g_track.audio.is_playing:
        #     action_list += "; waits {0}".format(g_track.beat_count_before_clip_restart - 1)

        if g_track.audio.is_playing:
            action_list += Actions.restart_grouped_track(g_track, g_track.audio)
        elif g_track.midi.is_playing:
            action_list += Actions.restart_grouped_track(g_track, g_track.midi)
            action_list += "{0}}"
        else:
            action_list += Actions.restart_grouped_track(g_track, None)

        action_list += "; waits 2; {0}/arm off".format(g_track.audio.index)

        if direct_unarm:
            action_list += "; push msg 'tracks {0} unarmed'".format(g_track.name)

        self.exec_action(action_list, None, "unarm_ext")

    def sel_ext(self, action_def, restart_clips=""):
        """ Sel midi track to open ext editor """
        self.song().restart_clips = bool(restart_clips)
        g_track = self.get_group_track(action_def, "sel_ext")

        if isinstance(g_track, Track) and g_track.is_foldable:
            return self.exec_action("{0}/fold {1}".format(g_track.index, "off" if g_track.is_folded else "on"), None, "sel_ext")

        action_list = ""
        if self.song().selected_track.track == g_track.selectable_track.track:
            action_list += "; {0}/fold on; {0}/sel".format(g_track.group.index)
            return self.exec_action(action_list, None, "sel_ext")

        action_list += Actions.restart_grouped_track(g_track)
        action_list += "; {0}/fold off; {1}/sel".format(g_track.group.index, g_track.selectable_track.index)
        if g_track.is_prophet:
            action_list += BomeCommands.SHOW_AND_ACTIVATE_REV2_EDITOR
        else:
            action_list += BomeCommands.SELECT_FIRST_VST
        action_list += Actions.arm_g_track(g_track)

        self.exec_action(action_list, None, "sel_ext")

    def stop_audio_ext(self, action_def, restart_clips=""):
        """ arm both midi and audio track """
        self.song().restart_clips = bool(restart_clips)
        g_track = self.get_group_track(action_def)

        action_list = Actions.restart_track_on_group_press(g_track.midi, None)
        action_list += Actions.stop_track(g_track.audio)

        self.exec_action(action_list, None, "stop_audio_ext")

    def record_ext(self, action_def, bar_count):
        """ record both midi and audio on group track """
        g_track = self.get_group_track(action_def)
        rec_clip_index = g_track.rec_clip_index
        action_list = Actions.arm_g_track(g_track)
        action_list += Actions.add_scene_if_needed(g_track.audio)

        action_list_rec = "; {0}/recfix {2} {3}; {1}/recfix {2} {3}; {0}/name '{3}'; {1}/name '{3}'".format(
            g_track.midi.index, g_track.audio.index, bar_count, rec_clip_index
        )
        action_list += Actions.restart_and_record(g_track, action_list_rec)
        # when done, stop audio clip and metronome
        delay = int(round((600 / self.song().tempo) * (4 * (int(bar_count) + 1) - 0.5)))
        action_list += "; wait {0}; {1}/stop; metro off; wait 5".format(delay, g_track.audio.index)

        # rename timestamp clip to link clips
        timestamp = time.time()
        action_list += "; {0}/clip({1}) name {2}".format(g_track.midi.index, rec_clip_index, timestamp)
        action_list += "; {0}/clip({1}) name {2}; {0}/clip({1}) warpmode complex".format(g_track.audio.index, rec_clip_index, timestamp)

        self.exec_action(action_list, g_track, "record_ext")

    def record_ext_audio(self, action_def, _):
        """ record audio on group track from playing midi clip """
        g_track = self.get_group_track(action_def, "", True)

        if not g_track.midi.is_playing:
            return self.log_to_push("midi not playing, cannot record audio")

        action_list = Actions.arm_g_track(g_track)
        action_list += Actions.add_scene_if_needed(g_track.audio)
        action_list += Actions.restart_track_on_group_press(g_track.midi)
        action_list_rec = "; {0}/recfix {1} {2}; {0}/name '{2}'".format(
            g_track.audio.index, int(round((g_track.midi.playing_clip.length + 1) / 4)), g_track.rec_clip_index
        )
        action_list += Actions.restart_and_record(g_track, action_list_rec, False)
        # when done, stop audio clip
        delay = int(round((600 / self.song().tempo) * (int(g_track.midi.playing_clip.length) + 6)))
        action_list += "; wait {0}; {1}/clip({2}) name '{3}'; {1}/clip({2}) warpmode complex".format(
            delay, g_track.audio.index, g_track.rec_clip_index, g_track.midi.playing_clip.name)
        action_list += Actions.set_audio_playing_color(g_track, Colors.PLAYING)

        self.exec_action(action_list, g_track, "record_ext_audio")

    def undo_ext(self, action_def):
        """" undo last recording """
        g_track = self.get_group_track(action_def)

        action_list = Actions.delete_playing_clips(g_track)
        self.exec_action(action_list, None, "undo_ext")

    def restart_ext(self, _):
        """" restart a live set from group tracks track names """
        action_list = "; ".join([Actions.restart_grouped_track(g_track) for g_track in self.song().group_ex_tracks])

        self.exec_action(action_list, None, "restart_ext")

