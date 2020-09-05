from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
import collections

class AbstractUserAction(UserActionsBase):
    def exec_action(self, action_list):
        self.canonical_parent.log_message('action_list %s' % action_list)
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)

    def get_group_track(self, action_def):
        track_index_clyphx = list(self.song().tracks).index(action_def['track']) + 1

        # check if we clicked on group track instead of clyphx track
        if list(self.song().tracks)[track_index_clyphx - 1].is_foldable:
            track_index_clyphx += 1
        track_index_midi = track_index_clyphx + 1
        track_index_audio = track_index_clyphx + 2

        midi_track = list(self.song().tracks)[track_index_midi - 1]
        audio_track = list(self.song().tracks)[track_index_audio - 1]

        GroupTrack = collections.namedtuple("Collection", [
            "index_clyphx", "index_midi", "index_audio", "midi", "audio"
        ])

        return GroupTrack(track_index_clyphx, track_index_midi, track_index_audio, midi_track, audio_track)

    def get_action_arm_tracks(self, action_def):
        g_track = self.get_group_track(action_def)

        return "{0}/arm off ; {1}/arm on ; {2}/arm on".format(
            g_track.index_clyphx, g_track.index_midi, g_track.index_audio
        )

    def add_scene_if_needed(self, audio_track):
        first_empty_clip_index = next(
            iter([i for i, clip_slot in enumerate(list(audio_track.clip_slots)) if clip_slot.clip is None]), None)

        return " ; addscene -1 ; wait 2" if first_empty_clip_index is None else ""

    def get_empty_scene_index(self, audio_track):
        first_empty_clip_index = next(
            iter([i for i, clip_slot in enumerate(list(audio_track.clip_slots)) if clip_slot.clip is None]), None)

        first_empty_clip_index + 1 if first_empty_clip_index is not None else len(
            list(audio_track.clip_slots)) + 1

        self.canonical_parent.log_message('clip free %s' % first_empty_clip_index)

        return first_empty_clip_index

    def get_playing_clips_count(self, action_def):
        g_track = self.get_group_track(action_def)

        playing_clips_count = len([clip_slot for index, track in enumerate(self.song().tracks)
                                   for clip_slot in track.clip_slots
                                   if index not in (g_track.index_midi - 1, g_track.index_audio - 1) and clip_slot.clip
                                   and not clip_slot.clip.name.startswith("[]")
                                   and clip_slot.clip.is_playing])

        self.canonical_parent.log_message('playing_clips_count %s' % playing_clips_count)