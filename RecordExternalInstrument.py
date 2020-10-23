import time

from ClyphX_Pro.clyphx_pro.user_actions.actions.Actions import Actions
from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions.utils.utils import for_all_methods, init_song
from ClyphX_Pro.clyphx_pro.user_actions.actions.AbstractUserAction import AbstractUserAction


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

    def arm_ext(self, action_def):
        """ arm or unarm both midi and audio track """
        if self.current_track.is_armed:
            return self.unarm_ext(action_def, "1")

        self.exec_action(self.current_track.action_arm(), self.current_track, "arm_ext")

    def unarm_ext(self, _, direct_unarm):
        """ unarming group track """
        self.exec_action(self.current_track.action_unarm(bool(direct_unarm)), None, "unarm_ext")

    def sel_ext(self):
        """ Sel midi track to open ext editor """
        self.exec_action(self.current_track.action_sel(), None, "sel_ext")

    def stop_audio_ext(self):
        """ arm both midi and audio track """
        self.exec_action(self.current_track.action_start_or_stop(), None, "stop_audio_ext")

    def record_ext(self, action_def, bar_count):
        """ record both midi and audio on group track """
        g_track = self.get_abstract_track(action_def['track'])
        rec_clip_index = g_track.rec_clip_index
        action_list = Actions.arm_g_track(g_track)
        action_list += Actions.add_scene_if_needed(g_track.audio)

        action_list_rec = "; {0}/recfix {2} {3}; {1}/recfix {2} {3}; {0}/name '{3}'; {1}/name '0'".format(
            g_track.midi.index, g_track.audio.index, bar_count, rec_clip_index
        )
        action_list += Actions.restart_and_record(g_track, action_list_rec)
        # when done, stop audio clip and metronome
        delay = int(round((600 / self.song().tempo) * (4 * (int(bar_count) + 1) - 0.5)))
        action_list += "; wait {0}; metro off; wait 5; {1}/stop".format(delay, g_track.audio.index)

        # rename timestamp clip to link clips
        timestamp = time.time()
        action_list += "; {0}/clip({1}) name {2}".format(g_track.midi.index, rec_clip_index, timestamp)
        action_list += "; {0}/clip({1}) name {2}; {0}/clip({1}) warpmode complex".format(g_track.audio.index, rec_clip_index, timestamp)

        self.exec_action(action_list, g_track, "record_ext")

    def record_ext_audio(self, action_def, _):
        """ record audio on group track from playing midi clip """
        g_track = self.get_abstract_track(action_def['track'], "", True)

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
        g_track = self.get_abstract_track(action_def['track'])

        action_list = Actions.delete_playing_clips(g_track)
        self.exec_action(action_list, None, "undo_ext")

    def restart_ext(self, _):
        """" restart a live set from group tracks track names """
        action_list = "; ".join([Actions.restart_grouped_track(g_track) for g_track in self.song().group_ex_tracks])

        self.exec_action(action_list, None, "restart_ext")

