# noinspection PyUnresolvedReferences
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase

from ClyphX_Pro.clyphx_pro.user_actions._Actions import Actions
from ClyphX_Pro.clyphx_pro.user_actions._GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions._Song import MySong


class AbstractUserAction(UserActionsBase):
    def __init__(self, *args, **kwargs):
        super(AbstractUserAction, self).__init__(*args, **kwargs)
        self.__song = None

    def mySong(self):
        # type: () -> MySong
        return self.__song if self.__song else self._song

    def get_group_track(self, action_def, action=None):
        # type: ([str], str) -> GroupTrack
        g_track = GroupTrack(self.mySong(), action_def['track'])
        # when actioning sel/sel_midi_ext from midi track to unselect midi track
        if action == "sel_midi_ext" and not g_track.is_group_track:
            g_track = GroupTrack(self.mySong(), self.mySong().tracks[g_track.group.index - 3])

        if not g_track.is_group_track and action not in ("sel_midi_ext", "next_ext", "prev_ext"):
            raise Exception("executed ex command on wrong track")

        return g_track

    def get_next_track_by_index(self, index, go_next, group=False):
        # type: (int, bool) -> GroupTrack
        tracks = self.mySong().group_ex_tracks if group else self.mySong().visible_tracks
        tracks = tracks if go_next else list(reversed(tracks))

        if len(tracks) == 0:
            raise Exception("No tracks in this set")

        for track in tracks:
            if go_next and track.index > index:
                return track
            elif not go_next and track.index < index:
                return track

        return tracks[0]

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

    def restart_and_record(self, g_track, action_list_rec, metro=True):
        # type: (GroupTrack, str, bool) -> str
        """ restart audio to get a count in and recfix"""
        action_list = "; setplay off"

        if not self.mySong().has_set_playing_clips(g_track, False) and metro:
            action_list += "; metro on"

        action_list += action_list_rec

        return action_list
