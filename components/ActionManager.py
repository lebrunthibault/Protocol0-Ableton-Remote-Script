from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import RECORDING_TIMES, TRACK_CATEGORIES, TRACK_CATEGORY_ALL
from a_protocol_0.controls.MultiEncoder import MultiEncoder
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.utils.decorators import button_action
from a_protocol_0.utils.utils import scroll_values, find_all_devices


class ActionManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(ActionManager, self).__init__(*a, **k)
        # SHiFT encoder
        MultiEncoder(channel=15, identifier=1,
                     on_press=lambda: setattr(MultiEncoder, "SHIFT_PRESSED", True),
                     on_release=lambda: setattr(MultiEncoder, "SHIFT_PRESSED", False)
                     )

        # TRacK encoder
        MultiEncoder(channel=15, identifier=13,
                     on_press=self.action_arm_track,
                     on_long_press=self.action_solo_track,
                     on_scroll=self.action_scroll_tracks)

        # PRESet encoder
        MultiEncoder(channel=15, identifier=14,
                     on_press=self.action_show_track_instrument,
                     on_scroll=self.action_scroll_track_instrument_presets,
                     on_shift_scroll=self.action_scroll_simpler_drum_categories
                     )

        # DEVice encoder
        MultiEncoder(channel=15, identifier=15,
                     on_press=self.action_track_collapse_selected_device,
                     on_scroll=self.action_scroll_track_devices)

        # CLIP encoder
        MultiEncoder(channel=15, identifier=16,
                     on_press=self.action_play_track,
                     on_scroll=self.action_scroll_track_clips)

        # RECord encoder
        MultiEncoder(channel=15, identifier=9,
                     on_press=self.action_track_record_fixed,
                     on_long_press=self.action_track_record_audio,
                     on_scroll=self.action_scroll_track_recording_times)

        # STOP encoder
        MultiEncoder(channel=15, identifier=11,
                     on_press=self.action_stop_track,
                     on_long_press=self.action_stop_category,
                     on_scroll=self.action_scroll_track_categories)

        # PLAY encoder
        MultiEncoder(channel=15, identifier=12,
                     on_press=self.action_play_track,
                     on_long_press=self.restart_category,
                     on_scroll=self.action_scroll_track_categories)

        # MONitor encoder
        MultiEncoder(channel=15, identifier=3,
                     on_press=self.action_switch_track_monitoring)

        # LFO encoder (add group track with lfo tool binding)
        MultiEncoder(channel=15, identifier=5,
                     on_press=self.action_set_up_lfo_tool_automation)

        # UNDO encoder
        MultiEncoder(channel=15, identifier=4,
                     on_press=self.action_undo)

    @button_action(log_action=False)
    def action_scroll_tracks(self, go_next):
        """ scroll top tracks """
        track_to_select = scroll_values(self.song.scrollable_tracks, self.song.current_track.base_track,
                                        go_next)  # type: SimpleTrack
        if track_to_select:
            if track_to_select.playable_clip:
                self.song.highlighted_clip_slot = track_to_select.playable_clip.clip_slot
            else:
                self.song.select_track(track_to_select)

    @button_action()
    def action_arm_track(self):
        """ arm or unarm both midi and audio track """
        if self.song.current_track.arm:
            self.song.current_track.action_unarm()
        else:
            self.song.current_track.action_arm()

    @button_action()
    def action_solo_track(self):
        [t.action_solo() for t in self.song.selected_tracks]

    @button_action()
    def action_show_track_instrument(self):
        """ Sel instrument track and open instrument window """
        self.song.current_track.action_show_instrument()

    @button_action(log_action=False)
    def action_scroll_track_instrument_presets(self, go_next):
        """ scroll track device presets or samples """
        self.parent.clyphxNavigationManager.show_track_view()
        if self.song.current_track.instrument:
            self.song.current_track.instrument.action_scroll_presets_or_samples(go_next)

    @button_action(log_action=False)
    def action_scroll_simpler_drum_categories(self, go_next):
        """ scroll track device presets or samples """
        self.parent.clyphxNavigationManager.show_track_view()
        if self.song.current_track.instrument:
            self.song.current_track.instrument.action_scroll_categories(go_next=go_next)

    @button_action(log_action=False)
    def action_scroll_track_devices(self, go_next):
        """ record both midi and audio on group track """
        self.parent.application().view.focus_view(u'Detail/DeviceChain')
        selected_device = scroll_values(find_all_devices(self.song.current_track, only_visible=True),
                                        self.song.current_track.selected_device, go_next)
        if selected_device:
            self.song.select_device(selected_device)

    @button_action(log_action=False)
    def action_track_collapse_selected_device(self):
        """ record both midi and audio on group track """
        self.song.current_track.selected_device.view.is_collapsed = not self.song.current_track.selected_device.view.is_collapsed

    @button_action(log_action=False)
    def action_scroll_track_recording_times(self, go_next):
        """ record both midi and audio on group track """
        self.song.selected_recording_time = scroll_values(RECORDING_TIMES, self.song.selected_recording_time, go_next)
        self.song.current_track.bar_count = int(self.song.selected_recording_time.split()[0])
        self.parent.show_message("Selected %s" % self.song.selected_recording_time)

    @button_action(auto_arm=True)
    def action_track_record_fixed(self):
        """ record both midi and audio on group track """
        self.song.current_track.action_restart_and_record(self.song.current_track.action_record_all)

    @button_action(auto_arm=True)
    def action_track_record_audio(self):
        """ record only audio on group track """
        return self.song.current_track.action_restart_and_record(self.song.current_track.action_record_audio_only,
                                                                 only_audio=True)

    @button_action(log_action=False)
    def action_scroll_track_categories(self, go_next):
        """" stop a live set from group tracks track names """
        self.song.selected_track_category = scroll_values(TRACK_CATEGORIES, self.song.selected_track_category, go_next)
        self.parent.show_message("Selected %s" % self.song.selected_track_category)

    @button_action()
    def action_stop_track(self):
        """" stop a live set from group tracks track names """
        [t.stop() for t in self.song.selected_tracks]

    @button_action()
    def action_stop_category(self):
        """" stop a live set from group tracks track names """
        if self.song.selected_track_category == TRACK_CATEGORY_ALL:
            self.song.stop_all_clips()
        else:
            [track.stop() for track in self.song.selected_category_tracks]
        self.parent.show_message("Stopping %s" % self.song.selected_track_category)

    @button_action(log_action=False)
    def action_scroll_track_clips(self, go_next):
        """" stop a live set from group tracks track names """
        self.song.selected_track.scroll_clips(go_next=go_next)

    @button_action()
    def action_play_track(self):
        [t.base_track.play() for t in self.song.selected_tracks]

    @button_action()
    def restart_category(self):
        """" restart a live set from group tracks track names """
        [track.play() for track in self.song.selected_category_tracks]
        self.parent.show_message("Starting %s" % self.song.selected_track_category)

    @button_action()
    def action_switch_track_monitoring(self):
        self.song.current_track.action_switch_monitoring()

    @button_action()
    def action_set_up_lfo_tool_automation(self):
        self.parent.trackAutomationManager.create_automation_group(self.song.current_track.base_track)

    @button_action()
    def action_undo(self):
        """" undo last recording """
        self.song.current_track.action_undo()
