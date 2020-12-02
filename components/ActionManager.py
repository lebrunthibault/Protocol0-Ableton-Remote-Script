from __future__ import with_statement

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import *
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import RECORDING_TIMES, TRACK_CATEGORIES, TRACK_CATEGORY_ALL
from a_protocol_0.controls.MultiEncoder import MultiEncoder
from a_protocol_0.utils.decorators import button_action
from a_protocol_0.utils.utils import scroll_values


class ActionManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(ActionManager, self).__init__(*a, **k)
        track_encoder = MultiEncoder(channel=15, identifier=13)
        track_encoder.on_scroll = self.action_scroll_tracks
        track_encoder.on_press = self.action_arm_track
        track_encoder.on_long_press = self.action_solo_track

        instrument_encoder = MultiEncoder(channel=15, identifier=14)
        instrument_encoder.on_scroll = self.action_scroll_track_instrument_presets
        instrument_encoder.on_press = self.action_show_track_instrument

        device_encoder = MultiEncoder(channel=15, identifier=15)
        device_encoder.on_scroll = self.action_scroll_track_devices

        record_encoder = MultiEncoder(channel=15, identifier=9)
        record_encoder.on_scroll = self.action_scroll_track_recording_times
        record_encoder.on_press = self.action_track_record_fixed
        record_encoder.on_long_press = self.action_track_record_audio

        stop_encoder = MultiEncoder(channel=15, identifier=11)
        stop_encoder.on_scroll = self.action_scroll_track_categories
        stop_encoder.on_press = self.stop_track
        stop_encoder.on_long_press = self.stop_category

        restart_encoder = MultiEncoder(channel=15, identifier=12)
        restart_encoder.on_scroll = self.action_scroll_track_categories_2
        restart_encoder.on_press = self.restart_track
        restart_encoder.on_long_press = self.restart_category

        self.action_switch_track_monitoring.subject = ButtonElement(True, MIDI_NOTE_TYPE, channel=15, identifier=3)
        self.action_undo.subject = ButtonElement(True, MIDI_NOTE_TYPE, channel=15, identifier=4)

    @button_action(is_scrollable=True, log_action=False)
    def action_scroll_tracks(self, go_next):
        """ scroll top tracks """
        self.song.scroll_tracks(go_next)

    @button_action()
    def action_arm_track(self):
        """ arm or unarm both midi and audio track """
        if self.current_track.is_simple_group:
            self.current_track.is_folded = not self.current_track.is_folded
            return

        if self.current_track.arm:
            self.current_track.action_unarm()
        else:
            self.current_track.action_arm()

    @button_action(auto_arm=True)
    def action_solo_track(self):
        self.current_track.action_solo()

    @button_action(is_scrollable=True, auto_arm=True)
    def action_scroll_track_instrument_presets(self, go_next):
        """ scroll track device presets or samples """
        self.current_track.instrument.action_scroll_presets_or_samples(go_next)

    @button_action()
    def action_show_track_instrument(self):
        """ Sel instrument track and open instrument window """
        self.current_track.action_show_instrument()

    @button_action(is_scrollable=True)
    def action_scroll_track_devices(self, go_next):
        """ record both midi and audio on group track """
        selected_device = scroll_values(self.current_track.all_devices, self.current_track.selected_device, go_next)
        if selected_device:
            self.song.select_device(selected_device)
            self.parent.log(selected_device.parameters)

    @button_action(is_scrollable=True)
    def action_scroll_track_recording_times(self, go_next):
        """ record both midi and audio on group track """
        self.current_track.selected_recording_time = scroll_values(RECORDING_TIMES, self.current_track.selected_recording_time, go_next)
        self.current_track.bar_count = int(self.current_track.selected_recording_time.split()[0])
        self.parent.show_message("Selected %s" % self.current_track.selected_recording_time)

    @button_action(auto_arm=True)
    def action_track_record_fixed(self):
        """ record both midi and audio on group track """
        self.current_track.action_restart_and_record(self.current_track.action_record_all)

    @button_action(auto_arm=True)
    def action_track_record_audio(self):
        """ record only audio on group track """
        return self.current_track.action_restart_and_record(self.current_track.action_record_audio_only, only_audio=True)

    @button_action(is_scrollable=True)
    def action_scroll_track_categories(self, go_next):
        """" stop a live set from group tracks track names """
        self.song.selected_track_category = scroll_values(TRACK_CATEGORIES, self.song.selected_track_category, go_next)
        self.parent.show_message("Selected %s" % self.song.selected_track_category)

    @button_action()
    def stop_track(self):
        """" stop a live set from group tracks track names """
        self.current_track.stop()

    @button_action()
    def stop_category(self):
        """" stop a live set from group tracks track names """
        if self.song.selected_track_category == TRACK_CATEGORY_ALL:
            self.song.stop_all_clips()
        else:
            [track.stop() for track in self.song.selected_category_tracks]
        self.parent.show_message("Stopping %s" % self.song.selected_track_category)

    @button_action(is_scrollable=True)
    def action_scroll_track_categories_2(self, go_next):
        """" stop a live set from group tracks track names """
        self.song.selected_track_category = scroll_values(TRACK_CATEGORIES, self.song.selected_track_category, go_next)
        self.parent.show_message("Selected %s" % self.song.selected_track_category)

    @button_action()
    def restart_track(self):
        """" restart a live set from group tracks track names """
        self.current_track.base_track.restart()

    @button_action()
    def restart_category(self):
        """" restart a live set from group tracks track names """
        [track.restart() for track in self.song.selected_category_tracks]
        self.parent.show_message("Starting %s" % self.song.selected_track_category)

    @button_action()
    def action_switch_track_monitoring(self):
        self.current_track.action_switch_monitoring()

    @button_action()
    def action_undo(self):
        """" undo last recording """
        self.current_track.action_undo()
