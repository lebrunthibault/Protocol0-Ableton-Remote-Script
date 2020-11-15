from a_protocol_0.Protocol0Component import Protocol0Component
from a_protocol_0.lom.Song import Song
from a_protocol_0.utils.decorators import for_all_methods, init_song, unarm_other_tracks


# noinspection PyUnusedLocal
@for_all_methods(init_song)
class RecordExternalInstrument(Protocol0Component):
    """ Utility commands to record fixed length midi and audio on separate tracks """

    def create_actions(self):
        self.add_global_action('scroll_selected_mode', self.scroll_selected_mode)
        self.add_global_action('scroll_tracks', self.scroll_tracks)
        self.add_global_action('scroll_presets', self.scroll_presets)
        self.add_global_action('arm_ext', self.arm_ext)
        self.add_global_action('unarm_ext', self.unarm_ext)
        self.add_global_action('sel_ext', self.sel_ext)
        self.add_global_action('switch_monitoring_ext', self.switch_monitoring_ext)
        self.add_global_action('record_ext', self.record_ext)
        self.add_global_action('record_audio_ext', self.record_audio_ext)
        self.add_global_action('undo_ext', self.undo_ext)
        self.add_global_action('restart_set', self.restart_set)
        self.add_global_action('rename_all_clips', self.rename_all_clips)

    def scroll_selected_mode(self, _, go_next="1"):
        """ scroll selected scroll mode """
        if Song.SCROLL_MODE == "tracks":
            self.mySong().scroll_tracks(bool(go_next))
        else:
            self.current_track.instrument.action_scroll_presets_or_samples(bool(go_next))

    def scroll_tracks(self, _, go_next="1"):
        """ scroll top tracks """
        Song.SCROLL_MODE = "tracks"
        self.mySong().scroll_tracks(bool(go_next))

    def scroll_presets(self, _, go_next=""):
        """ scroll track device presets or samples """
        Song.SCROLL_MODE = "presets"
        self.current_track.instrument.action_scroll_presets_or_samples(bool(go_next))

    @unarm_other_tracks
    def arm_ext(self, action_def, _):
        """ arm or unarm both midi and audio track """
        if self.current_track.arm:
            self.current_track.action_unarm()
        else:
            self.current_track.action_arm()

    def unarm_ext(self, _, direct_unarm):
        """ unarming group track """
        self.current_track.action_unarm()

    @unarm_other_tracks
    def sel_ext(self, *args):
        """ Sel midi track to open ext editor """
        self.current_track.action_sel()

    def switch_monitoring_ext(self, *args):
        """ arm both midi and audio track """
        self.current_track.switch_monitoring()

    @unarm_other_tracks
    def record_ext(self, _, bar_count):
        """ record both midi and audio on group track """
        self.mySong().bar_count = int(bar_count)
        self.current_track.action_restart_and_record(self.current_track.action_record_all)

    @unarm_other_tracks
    def record_audio_ext(self, *args):
        """ record audio on group track from playing midi clip """
        self.current_track.action_restart_and_record(self.current_track.action_record_audio_only)

    def undo_ext(self, *args):
        """" undo last recording """
        self.current_track.action_undo()

    def restart_set(self, *args):
        """" restart a live set from group tracks track names """
        self.mySong().restart_set()

    def rename_all_clips(self, *args):
        """" restart a live set from group tracks track names """
        self.mySong().rename_all_clips()
