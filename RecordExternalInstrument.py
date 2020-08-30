from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from ClyphX_Pro.clyphx_pro.user_actions._utils import print_except


class RecordExternalInstrument(UserActionsBase):
    """ Utility commands to record fixed length midi and audio on separate tracks """

    def create_actions(self):
        self.add_track_action('record_ext', self.track_action_record_external_instrument)
        self.add_track_action('record_ext_audio', self.track_action_record_external_instrument_audio)

    @print_except
    def track_action_record_external_instrument(self, action_def, bar_count):
        """ record both midi and audio on prophet grouped track """
        track_index_clyphx = list(self.song().tracks).index(action_def['track']) + 1
        track_index_midi = track_index_clyphx + 1
        track_index_audio = track_index_clyphx + 2
        audio_track = list(self.song().tracks)[track_index_clyphx + 1]

        action_list = "{0}/arm off ; {1}/arm on ; {2}/arm on".format(
            track_index_clyphx, track_index_midi, track_index_audio
        )
        action_list += " ; GQ 1 Bar"

        playing_clips_count = len([clip_slot for track in self.song().tracks
                                   for clip_slot in track.clip_slots
                                   if clip_slot.clip
                                   and not clip_slot.clip.name.startswith("[]")
                                   and clip_slot.clip.is_playing])

        first_empty_clip_index = next(
            iter([i for i, clip_slot in enumerate(list(audio_track.clip_slots)) if clip_slot.clip is None]), None)

        if first_empty_clip_index is None:
            action_list += " ; addscene -1 ; wait 2"
        if playing_clips_count == 0:
            action_list += " ; metro on"

        first_empty_clip_index = first_empty_clip_index + 1 if first_empty_clip_index is not None else len(
            list(audio_track.clip_slots)) + 1

        self.canonical_parent.log_message('clip free %s' % first_empty_clip_index)

        action_list += " ; {0}/recfix {2} {3} ; {1}/recfix {2} {3}".format(
            track_index_midi, track_index_audio, bar_count, first_empty_clip_index
        )
        action_list += " ; waits {0} ; {1}/stop ; metro off".format(int(bar_count) * 4 + 3, track_index_audio)
        self.canonical_parent.log_message('action_list %s' % action_list)
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)

    @print_except
    def track_action_record_external_instrument_audio(self, action_def, _):
        """ record audio on prophet grouped track from playing midi clip """
        track_index_clyphx = list(self.song().tracks).index(action_def['track']) + 1
        track_index_midi = track_index_clyphx + 1
        track_index_audio = track_index_clyphx + 2
        midi_track = list(self.song().tracks)[track_index_midi - 1]
        audio_track = list(self.song().tracks)[track_index_audio - 1]
        playing_midi_clip_slot = next(iter([clip_slot for clip_slot in list(midi_track.clip_slots) if
                                            clip_slot.has_clip and clip_slot.clip.is_playing]), None)

        if playing_midi_clip_slot is None:
            self.canonical_parent.log_message('Error: Tried to record audio when no midi clip is playing')
            self.canonical_parent.clyphx_pro_component.trigger_action_list(
                'push msg "Error: Tried to record audio when no midi clip is playing"')
            return

        bar_count = round(playing_midi_clip_slot.clip.length / 4)
        self.canonical_parent.log_message('bar_length %d' % bar_count)

        current_quantization = self.song().clip_trigger_quantization

        action_list = "{0}, {1}/arm off ; {2}/arm on".format(track_index_clyphx, track_index_midi, track_index_audio)

        first_empty_clip_index = next(
            iter([i for i, clip_slot in enumerate(list(audio_track.clip_slots)) if clip_slot.clip is None]), None)

        if first_empty_clip_index is None:
            action_list += " ; addscene -1 ; wait 2"

        first_empty_clip_index = first_empty_clip_index + 1 if first_empty_clip_index is not None else len(
            list(audio_track.clip_slots)) + 1

        self.canonical_parent.log_message('clip free %s' % first_empty_clip_index)

        action_list += " ; QG None ; setplay off; wait 10 ; {0}/recfix {2} {3} ; {1}/recfix {2} {3}; GQ {4}"\
            .format(track_index_midi, track_index_audio, bar_count, first_empty_clip_index, current_quantization)
        action_list += " ; waits {0} ; {1}/stop".format(bar_count * 4, track_index_audio)
        self.canonical_parent.log_message('action_list %s' % action_list)
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)
