import time

from ClyphX_Pro.clyphx_pro.user_actions._Actions import Actions
from ClyphX_Pro.clyphx_pro.user_actions._utils import for_all_methods, print_except
from ClyphX_Pro.clyphx_pro.user_actions._AbstractUserAction import AbstractUserAction


@for_all_methods(print_except)
class RecordExternalInstrument(AbstractUserAction):
    """ Utility commands to record fixed length midi and audio on separate tracks """

    def create_actions(self):
        self.add_track_action('arm_ext', self.arm_ext)
        self.add_track_action('sel_midi_ext', self.sel_midi_ext)
        self.add_track_action('stop_audio_ext', self.stop_audio_ext)
        self.add_track_action('clear_ext', self.clear_ext)
        self.add_track_action('record_ext', self.record_ext)
        self.add_track_action('record_ext_audio', self.record_ext_audio)

    def arm_ext(self, action_def, _):
        """ arm or unarm both midi and audio track """
        g_track = self.get_group_track(action_def)

        unarming = g_track.midi.arm and g_track.audio.arm

        if unarming:
            return self.unarm_ext(g_track)

        action_list = ""
        if g_track.is_playing:
            # sync all clips
            action_list += "; setplay on"
        action_list += Actions.restart_track_on_group_press(g_track.midi)
        # stop audio to have live synth parameter edition while midi is playing
        action_list += "; {0}/stop".format(g_track.audio.index) + Actions.set_audio_playing_color(g_track, AbstractUserAction.COLOR_DISABLED)
        # disable other clip colors
        for group_track in g_track.other_group_tracks:
            action_list += "; {0}/clip(1) color {1}".format(group_track.clyphx.index, AbstractUserAction.COLOR_DISABLED)
            action_list += "; {0}/fold on".format(group_track.group.index)
        # arm track
        action_list += Actions.arm_tracks(g_track) + \
            "; push msg 'tracks armed'; {0}/clip(1) color 1; ".format(g_track.clyphx.index)
        action_list += "; {0}/fold off; {1}/sel".format(g_track.group.index, g_track.midi.index)

        self.exec_action(action_list)

    def unarm_ext(self, g_track):
        """ unarming group track """
        action_list = "; {0}/arm on; {1}/arm off; {2}/arm off".format(
            g_track.clyphx.index, g_track.midi.index, g_track.audio.index)
        # restart audio to keep audio playback when unarming
        action_list += Actions.restart_audio_track_on_group_press(g_track)
        action_list += "; push msg 'tracks unarmed'; {0}/clip(1) color {1}; {2}/fold on".format(
            g_track.clyphx.index, AbstractUserAction.COLOR_DISABLED, g_track.group.index)
        action_list += "; wait 10; GQ {0}".format(int(self.song().clip_trigger_quantization) + 1)

        self.exec_action(action_list)

    def sel_midi_ext(self, action_def, _):
        """ Sel midi track to open ext editor """
        g_track = self.get_group_track(action_def)

        if self.song().view.selected_track == g_track.midi:
            return

        action_list = Actions.restart_grouped_track(g_track)
        action_list += "; {0}/fold off; {1}/sel".format(g_track.group.index, g_track.midi.index)
        action_list += "; ".join(["; {0}/fold on".format(group_track.group.index) for group_track in g_track.other_group_tracks])
        self.exec_action(action_list)

    def stop_audio_ext(self, action_def, _):
        """ arm both midi and audio track """
        g_track = self.get_group_track(action_def)

        action_list = "{0}/play {1}".format(g_track.midi.index, g_track.midi.playing_clip.index) if g_track.midi.is_playing else \
            "{0}/stop".format(g_track.midi.index)
        action_list += "; {0}/stop".format(g_track.audio.index)
        action_list += Actions.set_audio_playing_color(g_track, AbstractUserAction.COLOR_DISABLED)
        action_list += "; {0}/name '0'".format(g_track.audio.index)

        self.exec_action(action_list)

    def clear_ext(self, action_def, _):
        """ delete all clips on both midi and audio track """
        g_track = self.get_group_track(action_def)

        action_clear_midi = ["{0}/clip(" + str(index + 1) + ") del" for index, clip_slot in
                             enumerate(g_track.midi.track.clip_slots) if clip_slot.has_clip]
        action_clear_audio = ["{1}/clip(" + str(index + 1) + ") del" for index, clip_slot in
                              enumerate(g_track.audio.track.clip_slots) if clip_slot.has_clip]

        raw_action_list = "; ".join(action_clear_midi) + "; " + "; ".join(action_clear_audio)
        action_list = raw_action_list.format(g_track.midi.index, g_track.audio.index)
        action_list += "; metro off; waits 1; setstop; setjump 1.1.1"

        self.exec_action(action_list)

    def record_ext(self, action_def, bar_count):
        """ record both midi and audio on prophet grouped track """
        g_track = self.get_group_track(action_def)
        rec_clip_index = g_track.audio.rec_clip_index
        action_list = Actions.arm_tracks(g_track) + Actions.add_scene_if_needed(g_track.audio)

        action_list_rec = "; {0}/recfix {2} {3}; {1}/recfix {2} {3}; {0}/name '{3}'; {1}/name '{3}'".format(
            g_track.midi.index, g_track.audio.index, bar_count, rec_clip_index
        )
        action_list += self.restart_and_record(g_track, action_list_rec)
        # when done, stop audio clip and metronome
        delay = int(round((600 / self.song().tempo) * (4 * (int(bar_count) + 1) - 0.5)))
        action_list += "; wait {0}; {1}/stop; metro off; wait 5".format(delay, g_track.audio.index)

        # rename timestamp clip to link clips
        timestamp = time.time()
        action_list += "; {0}/clip({1}) name {2}".format(g_track.midi.index, rec_clip_index, timestamp)
        action_list += "; {0}/clip({1}) name {2}".format(g_track.audio.index, rec_clip_index, timestamp)

        self.exec_action(action_list)

    def record_ext_audio(self, action_def, _):
        """ record audio on prophet grouped track from playing midi clip """
        g_track = self.get_group_track(action_def)

        if not g_track.midi.is_playing:
            return self.log_push("midi not playing, cannot record audio")

        action_list = Actions.arm_tracks(g_track) + Actions.add_scene_if_needed(g_track.audio)
        action_list += "; {0}/play {1}".format(g_track.midi.index, g_track.midi.playing_clip.index)
        action_list_rec = "; {0}/recfix {1} {2}; {0}/name '{2}'".format(
            g_track.audio.index, int(round((g_track.midi.playing_clip.length + 1) / 4)), g_track.audio.rec_clip_index
        )
        action_list += self.restart_and_record(g_track, action_list_rec, False)
        # when done, stop audio clip
        delay = int(round((600 / self.song().tempo) * (int(g_track.midi.playing_clip.length) + 6)))
        action_list += "; wait {0}; {1}/clip({2}) name '{3}'".format(
            delay, g_track.audio.index, g_track.audio.rec_clip_index, g_track.midi.playing_clip.name)

        self.exec_action(action_list + Actions.set_audio_playing_color(g_track, AbstractUserAction.COLOR_PLAYING))
