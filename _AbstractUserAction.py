# noinspection PyUnresolvedReferences
from typing import Optional, Union

# noinspection PyUnresolvedReferences
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase

from ClyphX_Pro.clyphx_pro.user_actions._GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions._SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions._Song import Song
from ClyphX_Pro.clyphx_pro.user_actions._AbstractTrack import AbstractTrack


class AbstractUserAction(UserActionsBase):
    def __init__(self, *args, **kwargs):
        super(AbstractUserAction, self).__init__(*args, **kwargs)
        self._my_song = None

    def song(self):
        # type: () -> Song
        return self._my_song if self._my_song else self._song

    def get_group_track(self, action_def, action=None, strict_ext_check=False):
        # type: ([str], str, bool) -> AbstractTrack
        track = self.song().get_track(action_def['track'])
        if track.is_groupable:
            g_track = GroupTrack(self.song(), track.track)
        elif action == "sel_ext":
            # when actioning sel/sel_midi_ext from midi track to unselect midi track
            index = track.index - 4 if track.is_audio else track.index - 3
            g_track = GroupTrack(self.song(), self.song().tracks[index].track)
        elif strict_ext_check:
            raise Exception("executed ex command on wrong track")
        else:
            return track

        return g_track

    def get_next_track_by_index(self, index, go_next):
        # type: (int, bool) -> SimpleTrack
        tracks = self.song().top_tracks
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

    def log_to_push(self, message):
        # type: (str) -> None
        self.log(message)
        self.exec_action("; push msg %s" % message, None, "error")

    def exec_action(self, action_list, abstract_track=None, title="title missing"):
        # type: (str, Optional[AbstractTrack], str) -> None
        # e.g. when we call rec_ext without doing arm_ext first
        if title in ("arm_ext", "record_ext", "record_ext_audio") and self.song().other_armed_group_track(abstract_track):
            action_list += "; {0}/unarm_ext {1}".format(self.song().other_armed_group_track(abstract_track).group.index,
                                                        "1" if self.song().restart_clips else "")
            action_list =  ["; {0}/arm off".format(track.index) for track in self.song().simple_armed_tracks(abstract_track)]

        self.log("{0}: {1}".format(title, action_list))
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)
