# noinspection PyUnresolvedReferences
from typing import Optional, Union, Any

# noinspection PyUnresolvedReferences
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase

from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack


class AbstractUserAction(UserActionsBase):
    def __init__(self, *args, **kwargs):
        super(AbstractUserAction, self).__init__(*args, **kwargs)
        self._my_song = None
        self.current_track = None  # type: Optional[AbstractTrack]
        self.unarm_other_tracks = False  # type: bool
        self.action_name = ""  # type: str

    def song(self):
        # type: () -> Song
        return self._my_song if self._my_song else self._song

    def get_abstract_track(self, track, action=None, strict_ext_check=False):
        # type: (Any, str, bool) -> Union[SimpleTrack, GroupTrack]
        track = self.song().get_track(track)
        if track.is_groupable:
            return GroupTrack(self.song(), track.track)
        elif action == "sel_ext":
            # when actioning sel/sel_midi_ext from midi track to unselect midi track
            index = track.index - 4 if track.is_audio else track.index - 3
            return GroupTrack(self.song(), self.song().tracks[index].track)
        elif strict_ext_check:
            raise Exception("executed ex command on wrong track")
        else:
            return track

    def get_next_track_by_index(self, index, go_next):
        # type: (int, bool) -> SimpleTrack
        tracks = self.song().top_tracks if go_next else list(reversed(self.song().top_tracks))

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
        self.action_name = "error"
        self.exec_action("; push msg %s" % message)

    def exec_action(self, action_list):
        # type: (str) -> None
        # e.g. when we call rec_ext without doing arm_ext first
        if self.unarm_other_tracks:
            if self.song().other_armed_group_track(self.current_track):
                action_list += "; {0}/unarm_ext".format(self.song().other_armed_group_track(self.current_track).index)
            action_list += "; " + "; ".join(["{0}/arm off".format(track.index) for track in
                                             self.song().simple_armed_tracks(self.current_track)])
            self.unarm_other_tracks = False

        self.log("{0}: {1}".format(self.action_name, action_list))
        self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)
        self.action_name = None
