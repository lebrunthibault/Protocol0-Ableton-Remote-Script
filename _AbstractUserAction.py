# noinspection PyUnresolvedReferences
from typing import Optional, Union

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
        # type: ([str], str) -> Union[GroupTrack, Track]
        track = self.mySong().get_track(action_def['track'])
        if track.is_groupable:
            g_track = GroupTrack(self.mySong(), track.track)
        elif action == "sel_ext":
            # when actioning sel/sel_midi_ext from midi track to unselect midi track
            index = track.index - 4 if track.is_audio else track.index - 3
            g_track = GroupTrack(self.mySong(), self.mySong().tracks[index].track)
        else:
            return track

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
        # type: (str, Optional[GroupTrack], str) -> None
        # e.g. when we call rec_ext without doing arm_ext first
        if g_track:
            self.log("g_track.other_armed_group_track %s" % g_track.other_armed_group_track)
        if g_track and g_track.other_armed_group_track and title != "stop_audio_ext":
            self.log("calling unarm ext from exec_action on %s" % g_track.other_armed_group_track.index)
            action_list += "; {0}/unarm_ext {1}".format(g_track.other_armed_group_track.group.index,
                                                        "1" if g_track.song.restart_clips else "")

        self.log("{0}: {1}".format(title, action_list))
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)
