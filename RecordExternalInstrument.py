from ClyphX_Pro.clyphx_pro.user_actions.actions.AbstractUserAction import AbstractUserAction
from ClyphX_Pro.clyphx_pro.user_actions.utils.utils import for_all_methods, init_song, unarm_other_tracks


# noinspection PyUnusedLocal
@for_all_methods(init_song)
class RecordExternalInstrument(AbstractUserAction):
    """ Utility commands to record fixed length midi and audio on separate tracks """

    def create_actions(self):
        self.add_global_action('next_ext', self.next_ext)
        self.add_track_action('arm_ext', self.arm_ext)
        self.add_track_action('unarm_ext', self.unarm_ext)
        self.add_track_action('sel_ext', self.sel_ext)
        self.add_track_action('switch_monitoring_ext', self.switch_monitoring_ext)
        self.add_track_action('record_ext', self.record_ext)
        self.add_track_action('record_audio_ext', self.record_audio_ext)
        self.add_track_action('undo_ext', self.undo_ext)
        self.add_track_action('restart_ext', self.restart_ext)

    def next_ext(self, _, go_next="1"):
        """ arm or unarm both midi and audio track """
        selected_track_index = self.song().selected_track.index if self.song().selected_track else 0
        action_list = "; {0}/sel".format(self.get_next_track_by_index(selected_track_index, bool(go_next)).index)
        self.exec_action(action_list)

    @unarm_other_tracks
    def arm_ext(self, action_def, _):
        """ arm or unarm both midi and audio track """
        if self.current_track.is_armed:
            return self.unarm_ext(action_def, "1")

        if not self.current_track.can_be_armed:
            return

        self.exec_action(self.current_track.action_arm)

    def unarm_ext(self, _, direct_unarm):
        """ unarming group track """
        self.exec_action(self.current_track.action_unarm(bool(direct_unarm)))

    @unarm_other_tracks
    def sel_ext(self, *args):
        """ Sel midi track to open ext editor """
        self.exec_action(self.current_track.action_sel)

    def switch_monitoring_ext(self, *args):
        """ arm both midi and audio track """
        self.exec_action(self.current_track.action_switch_monitoring)

    @unarm_other_tracks
    def record_ext(self, _, bar_count):
        """ record both midi and audio on group track """
        action_list = self.current_track.action_undo if self.current_track.is_recording else ""
        self.song().bar_count = int(bar_count)
        self.exec_action(action_list + self.current_track.action_restart_and_record(self.current_track.action_record_all))

    @unarm_other_tracks
    def record_audio_ext(self, *args):
        """ record audio on group track from playing midi clip """
        self.exec_action(self.current_track.action_restart_and_record(self.current_track.action_record_audio_only))

    def undo_ext(self, *args):
        """" undo last recording """
        self.exec_action(self.current_track.action_undo)

    def restart_ext(self, *args):
        """" restart a live set from group tracks track names """
        action_list = "".join([track.action_restart for track in self.song().tracks])
        action_list = "setplay on" + action_list if action_list else ""

        self.exec_action(action_list)
