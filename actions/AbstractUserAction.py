import sys

from ClyphX_Pro.clyphx_pro.user_actions.utils.log import log_ableton

sys.path.insert(0, "C:\Python27\Lib\site-packages")
sys.path.insert(0, "C:\Python27")
sys.path.insert(0, "C:\Python27\Lib")
from ClyphX_Pro.clyphx_pro.UserActionsBase import UserActionsBase
from typing import Optional, Union, Any, Callable

from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack


# noinspection PyAbstractClass
class AbstractUserAction(UserActionsBase):
    xmode = 1

    def __init__(self, *args, **kwargs):
        super(AbstractUserAction, self).__init__(*args, **kwargs)
        self._my_song = None
        self.current_track = None  # type: Optional[AbstractTrack]
        self.unarm_other_tracks = False  # type: bool

    def song(self):
        # type: () -> Song
        return self._my_song if self._my_song else self._song

    def get_abstract_track(self, track):
        # type: (Any) -> Union[SimpleTrack, GroupTrack]
        track = self.song().get_track(track)
        if track.is_groupable:
            return GroupTrack(self.song(), track.track)
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

    def schedule_message(self, wait_time, message):
        # type: (int, Callable) -> None
        self.canonical_parent.schedule_message(wait_time, message)

    def wait_bars(self, bar_count, message):
        # type: (int, Callable) -> None
        self.canonical_parent.schedule_message(self.song().delay_before_recording_end(bar_count), message)

    def wait(self, ticks_count, message):
        # type: (int, Callable) -> None
        self.canonical_parent.schedule_message(ticks_count, message)

    def log_to_push(self, message):
        # type: (str) -> None
        self.log(message)
        self.exec_action("; push msg %s" % message, "push msg")

    def exec_action(self, action_list, title=None):
        # type: (Optional[str], Optional[str]) -> None
        if self.unarm_other_tracks:
            if self.song().other_armed_group_track(self.current_track):
                self.song().other_armed_group_track(self.current_track).action_unarm()
            for simple_track in self.song().simple_armed_tracks(self.current_track):
                simple_track.action_unarm()
            self.unarm_other_tracks = False

        if action_list:
            self.log("{0}: {1}".format(title if title else self.song().current_action_name, action_list))
            self.canonical_parent.clyphx_pro_component.trigger_action_list(action_list)
        else:
            log_ableton(self.song().current_action_name)

        # self.song().current_action_name = None
