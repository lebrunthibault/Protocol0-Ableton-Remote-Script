# noinspection PyUnresolvedReferences
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase

from ClyphX_Pro.clyphx_pro.user_actions._Actions import Actions
from ClyphX_Pro.clyphx_pro.user_actions._GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions._Track import Track
from ClyphX_Pro.clyphx_pro.user_actions._TrackName import TrackName


class AbstractUserAction(UserActionsBase):
    def get_group_track(self, action_def, action=None):
        # type: ([str], str) -> GroupTrack
        g_track = GroupTrack(self.song(), action_def['track'])
        # when actioning sel/sel_midi_ext from midi track to unselect midi track
        if action == "sel_midi_ext" and not g_track.is_group_track:
            midi_track_index = list(self.song().tracks).index(g_track.group.track)
            g_track = GroupTrack(self.song(), self.song().tracks[midi_track_index - 1])

        if not g_track.is_group_track and action not in ("sel_midi_ext", "next_ext", "prev_ext"):
            raise Exception("executed ex command on wrong track")

        return g_track

    def get_all_group_tracks(self):
        # type: () -> list[GroupTrack]
        return [GroupTrack(self.song(), track) for track in self.song().tracks if track.name in TrackName.GROUP_EXT_NAMES]

    def get_next_track_by_index(self, index, go_next, group=False):
        # type: (int, bool) -> GroupTrack
        tracks = self.get_all_group_tracks() if group else self.get_all_visible_tracks()
        tracks = tracks if go_next else list(reversed(tracks))

        if len(tracks) == 0:
            raise Exception("No tracks in this set")

        for track in tracks:
            if go_next and track.index > index:
                return track
            elif not go_next and track.index < index:
                return track

        return tracks[0]

    def get_all_visible_tracks(self):
        # type: () -> list[Track]
        return [Track(track, i + 1) for i, track in enumerate(list(self.song().tracks)) if track.is_visible]

    def get_all_armed_tracks(self):
        # type: () -> list[Track]
        return [Track(track, i + 1) for i, track in enumerate(list(self.song().tracks)) if track.can_be_armed and track.arm]

    def log(self, message):
        # type: (str) -> None
        self.canonical_parent.log_message(message)

    def log_to_push(self, g_track, message):
        # type: (GroupTrack, str) -> None
        self.log(message)

        action_list = ""

        if g_track and g_track.is_group_track:
            action_list += "setplay on"
            action_list += Actions.restart_grouped_track(g_track)

        self.exec_action(action_list + "; push msg %s" % message, None, "error")

    def exec_action(self, action_list, g_track=None, title="title missing"):
        # type: (str, GroupTrack, str) -> None
        # self.log("g_track.other_group_tracks: %s" % len(g_track.other_group_tracks))
        # self.log("g_track.other_armed_group_track: %s" % g_track.other_armed_group_track)
        if g_track and g_track.other_armed_group_track and title != "stop_audio_ext":
            action_list += "; {0}/unarm_ext".format(g_track.other_armed_group_track.group.index)

        self.log("{0}: {1}".format(title, action_list))
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)

    def get_playing_clips_count(self, g_track, include_group):
        # type: (GroupTrack, bool) -> int
        """ number of playing clip count in the live set excluding the group track """
        playing_clips_count = len([clip_slot for index, track in enumerate(self.song().tracks)
                                   for clip_slot in track.clip_slots
                                   if (include_group is True or index not in (
                                       g_track.midi.index - 1, g_track.audio.index - 1))
                                   and clip_slot.clip
                                   and not clip_slot.clip.name.startswith("[]")
                                   and clip_slot.clip.is_playing])

        return playing_clips_count

    def get_other_group_ex_tracks(self, base_track):
        """ get duplicate clyphx index and track from a base ex track """
        return [(i + 1, track) for (i, track) in enumerate(self.song().tracks) if
                track.name == base_track.name and track != base_track.track]

    def has_set_playing_clips(self, g_track, include_group=True):
        # type: (GroupTrack, bool) -> bool
        """ find if there is playing clips elsewhere
            by default checks also in group track
        """
        return self.get_playing_clips_count(g_track, include_group) != 0

    def restart_and_record(self, g_track, action_list_rec, metro=True):
        # type: (GroupTrack, str, bool) -> str
        """ restart audio to get a count in and recfix"""
        action_list = "; setplay off"

        if not self.has_set_playing_clips(g_track, False) and metro:
            action_list += "; metro on"

        action_list += action_list_rec

        return action_list
