from functools import partial

from a_protocol_0.components.actionManagers.AbstractActionManager import AbstractActionManager
from a_protocol_0.consts import RECORDING_TIMES, TRACK_CATEGORIES, TRACK_CATEGORY_ALL, PLAY_MENU_OPTIONS
from a_protocol_0.lom.device.PluginDevice import PluginDevice
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.utils.decorators import button_action
from a_protocol_0.utils.utils import scroll_values


class ActionManager(AbstractActionManager):
    """
        Main manager: gathering most the functionnalities. My faithful companion when producing on Live !
    """
    def __init__(self, *a, **k):
        super(ActionManager, self).__init__(channel=15, has_shift=True, record_actions_as_global=True, *a, **k)
        # FOLD encoder
        self.add_encoder(identifier=2, on_press=self.action_fold_track, on_long_press=self.action_fold_tracks)

        # MONitor encoder
        self.add_encoder(identifier=3, on_press=self.action_switch_track_monitoring)

        # UNDO encoder
        self.add_encoder(identifier=4, on_press=self.action_undo)

        # LFO encoder (add group track with lfo tool binding)
        self.add_encoder(identifier=5, on_press=self.action_set_up_lfo_tool_automation)

        # RECord encoder
        self.add_encoder(identifier=9,
                         on_press=self.action_track_record_fixed,
                         on_long_press=self.action_track_record_audio,
                         on_scroll=self.action_scroll_track_recording_times)

        # STOP encoder
        self.add_encoder(identifier=11,
                         on_press=self.action_stop_track,
                         on_long_press=self.action_stop_category,
                         on_scroll=self.action_scroll_track_categories)

        # PLAY encoder
        self.add_encoder(identifier=12,
                         on_press=self.action_play_selected_tracks,
                         on_shift_press=self.action_solo_play_selected_tracks,
                         on_long_press=self.action_restart_category,
                         on_scroll=self.action_scroll_track_categories)

        # TRacK encoder
        self.add_encoder(identifier=13,
                         on_press=self.action_arm_track,
                         on_long_press=self.action_solo_track,
                         on_shift_long_press=self.action_un_solo_all_tracks,
                         on_scroll=self.action_scroll_tracks)

        # PRESet encoder
        self.add_encoder(identifier=14,
                         on_press=self.action_show_track_instrument,
                         on_scroll=self.action_scroll_track_instrument_presets,
                         on_shift_scroll=self.action_scroll_simpler_drum_categories)

        # DEVice encoder
        self.add_encoder(identifier=15,
                         on_press=self.action_track_collapse_selected_device,
                         on_scroll=self.action_scroll_track_devices,
                         on_shift_scroll=self.action_scroll_selected_device_presets)

        # CLIP encoder
        self.add_encoder(identifier=16,
                         on_press=self.action_play_selected_tracks,
                         on_scroll=self.action_scroll_track_clips)

    @button_action(log_action=False)
    def action_scroll_tracks(self, go_next):
        """ scroll top tracks """
        base_track = self.song.selected_track if self.song.selected_track.is_scrollable else self.song.current_track.base_track
        track_to_select = scroll_values(self.song.scrollable_tracks, base_track, go_next)  # type: SimpleTrack
        if track_to_select:
            track_to_select.select()

    @button_action()
    def action_arm_track(self):
        """ arm or unarm both midi and audio track """
        if self.song.current_track.arm:
            return self.song.current_track.action_unarm()
        else:
            return self.song.current_track.action_arm()

    @button_action()
    def action_solo_track(self):
        [t.action_solo() for t in self.song.selected_tracks]

    @button_action()
    def action_un_solo_all_tracks(self):
        self.song.unsolo_all_tracks(except_current=False)

    @button_action()
    def action_show_track_instrument(self):
        """ Sel instrument track and open instrument window """
        self.song.current_track.action_show_hide_instrument()

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
        self.parent.clyphxNavigationManager.focus_detail()
        selected_device = scroll_values(self.song.current_track.base_track.all_visible_devices,
                                        self.song.current_track.selected_device, go_next)
        if selected_device:
            self.song.select_device(selected_device)

    @button_action(log_action=False)
    def action_scroll_selected_device_presets(self, go_next):
        """ record both midi and audio on group track """
        self.parent.clyphxNavigationManager.focus_detail()

        if not isinstance(self.song.current_track.selected_device, PluginDevice):
            self.parent.show_message("Presets scrolling is only available for plugin devices")
            return

        selected_device = self.song.current_track.selected_device  # type: PluginDevice
        selected_device.is_collapsed = False
        selected_device.selected_preset_index = scroll_values(selected_device.presets, selected_device.selected_preset,
                                                              go_next, return_index=True)

    @button_action(log_action=False)
    def action_track_collapse_selected_device(self):
        """ record both midi and audio on group track """
        if not self.song.current_track.selected_device:
            return
        self.song.current_track.selected_device.is_collapsed = not self.song.current_track.selected_device.is_collapsed

    @button_action(log_action=False)
    def action_scroll_track_recording_times(self, go_next):
        """ record both midi and audio on group track """
        self.song.selected_recording_time = scroll_values(RECORDING_TIMES, self.song.selected_recording_time, go_next)
        self.song.recording_bar_count = int(self.song.selected_recording_time.split()[0])
        self.parent.show_message("Selected %s" % self.song.selected_recording_time)

    @button_action(auto_arm=True)
    def action_track_record_fixed(self):
        """ record both midi and audio on group track """
        self.song.current_track.action_restart_and_record(self.song.current_track.action_record_all)

    @button_action(auto_arm=True)
    def action_track_record_audio(self):
        """ record only audio on group track """
        return self.song.current_track.action_restart_and_record(self.song.current_track.action_record_audio_only)

    @button_action(log_action=False)
    def action_scroll_track_categories(self, go_next):
        """" stop a live set from group tracks track names """
        options = TRACK_CATEGORIES + (PLAY_MENU_OPTIONS if self.song.has_solo_selection else [])
        self.song.selected_track_category = scroll_values(options, self.song.selected_track_category, go_next)
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
    def action_play_selected_tracks(self):
        [t.base_track.play() for t in self.song.selected_tracks]

    @button_action()
    def action_solo_play_selected_tracks(self):
        self.parent.playTrackManager.action_solo_play_selected_tracks()

    @button_action()
    def action_restart_category(self):
        """" restart a live set from group tracks track names """
        if self.song.has_solo_selection and self.song.selected_track_category in PLAY_MENU_OPTIONS:
            self.parent.playTrackManager.handle_play_menu_click()
        else:
            [track.play() for track in self.song.selected_category_tracks]
            self.parent.show_message("Starting %s" % self.song.selected_track_category)

    @button_action()
    def action_switch_track_monitoring(self):
        self.song.current_track.action_switch_monitoring()

    @button_action()
    def action_set_up_lfo_tool_automation(self):
        self.parent.automationTrackManager.create_automation_group(self.song.selected_parameter)

    @button_action()
    def action_fold_track(self):
        """" undo last recording """
        self.song.current_track.is_folded = not self.song.current_track.is_folded

    @button_action()
    def action_fold_tracks(self):
        """" undo last recording """
        self.song.fold_all_tracks()

    @button_action()
    def action_undo(self):
        """" undo last recording """
        self.song.current_track.action_undo()
