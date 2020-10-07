# noinspection PyUnresolvedReferences
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase

from ClyphX_Pro.clyphx_pro.user_actions._Actions import Actions
from ClyphX_Pro.clyphx_pro.user_actions._GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions._Song import Song
from ClyphX_Pro.clyphx_pro.user_actions._Track import Track


class AbstractUserAction(UserActionsBase):
    def __init__(self, *args, **kwargs):
        super(AbstractUserAction, self).__init__(*args, **kwargs)
        self._my_song = None

    def mySong(self):
        # type: () -> Song
        return self._my_song if self._my_song else self._song

    def get_group_track(self, action_def, action=None):
        # type: ([str], str) -> GroupTrack
        track = self.mySong().get_track(action_def['track'])
        if track.is_group or track.is_clyphx:
            g_track = GroupTrack(self.mySong(), track.track)
        elif action == "sel_ext":
            # when actioning sel/sel_midi_ext from midi track to unselect midi track
            index = track.index - 4 if track.is_audio else track.index - 3
            g_track = GroupTrack(self.mySong(), self.mySong().tracks[index].track)
        else:
            raise Exception("executed ex command on wrong track")

        return g_track

    def get_next_track_by_index(self, index, go_next):
        # type: (int, bool) -> Track
        tracks = self.mySong().top_tracks
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
        if g_track and g_track.other_armed_group_track and title != "stop_audio_ext":
            action_list += "; {0}/unarm_ext".format(g_track.other_armed_group_track.group.index)

        self.log("{0}: {1}".format(title, action_list))
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)
