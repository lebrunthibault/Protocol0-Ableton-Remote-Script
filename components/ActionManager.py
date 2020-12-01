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
        record_encoder = MultiEncoder(channel=15, identifier=9)
        record_encoder.on_scroll = self.scroll_recording_times
        record_encoder.on_press = self.record_ext
        record_encoder.on_long_press = self.record_ext_audio

        track_encoder = MultiEncoder(channel=15, identifier=13)
        track_encoder.on_scroll = self.scroll_tracks
        track_encoder.on_press = self.arm_ext
        track_encoder.on_long_press = self.solo_ext

        device_encoder = MultiEncoder(channel=15, identifier=14)
        device_encoder.on_scroll = self.scroll_presets
        device_encoder.on_press = self.sel_ext

        self.switch_monitoring_ext.subject = ButtonElement(True, MIDI_NOTE_TYPE, channel=15, identifier=3)

        restart_encoder = MultiEncoder(channel=15, identifier=12)
        restart_encoder.on_scroll = self.scroll_track_categories
        restart_encoder.on_press = self.restart_track
        restart_encoder.on_long_press = self.restart_category

        stop_encoder = MultiEncoder(channel=15, identifier=11)
        stop_encoder.on_scroll = self.scroll_track_categories_2
        stop_encoder.on_press = self.stop_track
        stop_encoder.on_long_press = self.stop_category
        self.undo_ext.subject = ButtonElement(True, MIDI_NOTE_TYPE, channel=15, identifier=16)

    @button_action()
    def arm_ext(self):
        """ arm or unarm both midi and audio track """
        if self.current_track.is_simple_group:
            self.current_track.is_folded = not self.current_track.is_folded
            return

        if self.current_track.arm:
            self.current_track.action_unarm()
        else:
            self.current_track.action_arm()

    @button_action()
    def sel_ext(self):
        """ Sel instrument track to open ext editor """
        self.current_track.action_sel()

    @button_action(auto_arm=True)
    def solo_ext(self):
        self.current_track.action_solo()

    @button_action()
    def switch_monitoring_ext(self):
        self.current_track.action_switch_monitoring()

    @button_action(is_scrollable=True)
    def scroll_recording_times(self, go_next):
        """ record both midi and audio on group track """
        self.current_track.selected_recording_time = scroll_values(RECORDING_TIMES, self.current_track.selected_recording_time, go_next)
        self.current_track.bar_count = int(self.current_track.selected_recording_time.split()[0])
        self.parent.show_message("Selected %s" % self.current_track.selected_recording_time)

    @button_action(auto_arm=True)
    def record_ext(self):
        """ record both midi and audio on group track """
        self.current_track.action_restart_and_record(self.current_track.action_record_all)

    @button_action(auto_arm=True)
    def record_ext_audio(self):
        """ record only audio on group track """
        return self.current_track.action_restart_and_record(self.current_track.action_record_audio_only, only_audio=True)

    @button_action(is_scrollable=True)
    def scroll_track_categories(self, go_next):
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

    @button_action(is_scrollable=True)
    def scroll_track_categories_2(self, go_next):
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

    @button_action()
    def undo_ext(self):
        """" undo last recording """
        self.current_track.action_undo()

    @button_action(is_scrollable=True, log_action=False)
    def scroll_tracks(self, go_next):
        """ scroll top tracks """
        self.song.scroll_tracks(go_next)

    @button_action(is_scrollable=True, auto_arm=True)
    def scroll_presets(self, go_next):
        """ scroll track device presets or samples """
        self.current_track.instrument.action_scroll_presets_or_samples(go_next)
