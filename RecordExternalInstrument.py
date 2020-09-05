from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from ClyphX_Pro.clyphx_pro.user_actions._utils import for_all_methods, print_except
from ClyphX_Pro.clyphx_pro.user_actions._AbstractUserAction import AbstractUserAction


@for_all_methods(print_except)
class RecordExternalInstrument(AbstractUserAction):
    """ Utility commands to record fixed length midi and audio on separate tracks """

    def create_actions(self):
        self.add_track_action('arm_ext', self.arm_ext)
        self.add_track_action('clear_ext', self.clear_ext)
        self.add_track_action('record_ext', self.record_ext)
        self.add_track_action('record_ext_audio', self.record_ext_audio)

    def arm_ext(self, action_def, _):
        """ arm both midi and audio track """
        self.exec_action(self.get_action_arm_tracks(action_def))

    def clear_ext(self, action_def, _):
        """ delete all clips on both midi and audio track """
        g_track = self.get_group_track(action_def)

        action_clear_midi = ["{0}/clip(" + str(index + 1) + ") del" for index, clip_slot in enumerate(g_track.midi.clip_slots) if clip_slot.has_clip]
        action_clear_audio = ["{1}/clip(" + str(index + 1) + ") del" for index, clip_slot in enumerate(g_track.audio.clip_slots) if clip_slot.has_clip]

        raw_action_list = " ; ".join(action_clear_midi) + " ; " + " ; ".join(action_clear_audio)
        action_list = raw_action_list.format(g_track.index_midi, g_track.index_audio)
        action_list += " ; metro off ; waits 1 ; setstop ; setjump 1.1.1"

        self.exec_action(action_list)

    def record_ext(self, action_def, bar_count):
        """ record both midi and audio on prophet grouped track """
        g_track = self.get_group_track(action_def)

        action_list = "setjump 1.1.2 ; metro on ; " if self.get_playing_clips_count(action_def) == 0 else ""

        action_list += self.get_action_arm_tracks(action_def) + self.add_scene_if_needed(g_track.audio)
        action_list += " ; {0}/recfix {2} {3} ; {1}/recfix {2} {3}".format(
            g_track.index_midi, g_track.index_audio, bar_count, self.get_empty_scene_index(g_track.audio)
        )
        action_list += " ; waits {0} ; {1}/stop ; metro off".format(int(bar_count) * 4 + 3, g_track.index_audio)

        self.exec_action(action_list)

    def record_ext_audio(self, action_def, _):
        """ record audio on prophet grouped track from playing midi clip """
        g_track = self.get_group_track(action_def)

        playing_midi_clip_slot = next(iter([clip_slot for clip_slot in list(g_track.midi.clip_slots) if
                                            clip_slot.has_clip and clip_slot.clip.is_playing]), None)

        if playing_midi_clip_slot is None:
            raise Exception("Error: Tried to record audio when no midi clip is playing")

        bar_count = round(playing_midi_clip_slot.clip.length / 4)

        action_list = self.get_action_arm_tracks(action_def) + self.add_scene_if_needed(g_track.audio)
        action_list += " ; QG None ; setplay off; wait 10 ; {0}/recfix {1} {2}; GQ {3}"\
            .format(g_track.index_audio, bar_count, self.get_empty_scene_index(g_track.audio), self.song().clip_trigger_quantization)
        action_list += " ; waits {0} ; {1}/stop".format(bar_count * 4, g_track.index_audio)

        self.exec_action(action_list)
