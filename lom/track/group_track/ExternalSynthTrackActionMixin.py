from functools import partial

from typing import TYPE_CHECKING, Optional

from protocol0.components.TrackDataManager import save_track_data
from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.enums.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import single_undo
from protocol0.utils.utils import scroll_values

if TYPE_CHECKING:
    from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


# noinspection PyTypeHints
class ExternalSynthTrackActionMixin(object):
    def arm_track(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        self.base_track.is_folded = False
        self.base_track.mute = False

        # checking levels
        self.audio_track._output_meter_level_listener.subject = self.audio_track._track

        if self.song.usamo_track:
            self.song.usamo_track.input_routing_track = self.midi_track

        self.midi_track.input_routing_type = self.instrument.MIDI_INPUT_ROUTING_TYPE

        seq = Sequence()
        seq.add([sub_track.arm for sub_track in self.sub_tracks if not isinstance(sub_track, SimpleDummyTrack)])
        seq.add(partial(setattr, self, "has_monitor_in", False))
        return seq.done()

    def unarm_track(self):
        # type: (ExternalSynthTrack) -> None
        self.has_monitor_in = True
        self.audio_track._output_meter_level_listener.subject = None

    @property
    def has_monitor_in(self):
        # type: (ExternalSynthTrack) -> bool
        return self.midi_track.mute is True

    # noinspection DuplicatedCode
    @has_monitor_in.setter
    @single_undo
    def has_monitor_in(self, has_monitor_in):
        # type: (ExternalSynthTrack, bool) -> None
        # unarm / listen to audio
        if has_monitor_in:
            self.midi_track.mute = True
            self.midi_track.current_monitoring_state = CurrentMonitoringStateEnum.IN

            self.audio_track.mute = False
            if self.midi_track.solo:
                self.audio_track.solo = True
                self.midi_track.solo = False
            self.audio_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO

            if self.audio_tail_track:
                self.audio_tail_track.mute = False
                self.audio_tail_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO

            if self._external_device:
                self._external_device.device_on = False
        # arm / listen to midi
        else:
            self.midi_track.mute = False
            if self.audio_track.solo:
                self.midi_track.solo = True
                self.audio_track.solo = False
            self.midi_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO

            self.audio_track.mute = True
            self.audio_track.current_monitoring_state = CurrentMonitoringStateEnum.IN

            if self.audio_tail_track:
                self.audio_tail_track.mute = True
                self.audio_tail_track.current_monitoring_state = CurrentMonitoringStateEnum.IN

            if self._external_device:
                self._external_device.device_on = True

    def switch_monitoring(self):
        # type: (ExternalSynthTrack) -> None
        self.has_monitor_in = not self.has_monitor_in

    @save_track_data
    def toggle_record_clip_tails(self):
        # type: (ExternalSynthTrack) -> None
        if not self._validate_has_record_clip_tails():
            return None

        self.record_clip_tails = not self.record_clip_tails
        message = "Record clip tails"
        if self.record_clip_tails:
            message += " ON"
            if self.record_clip_tails_bar_length != 1:
                message += " (%s)" % BarLengthEnum.int_to_str(self.record_clip_tails_bar_length)
        else:
            message += " OFF"
        self.parent.show_message(message)

    @save_track_data
    def scroll_record_clip_tails(self, go_next):
        # type: (ExternalSynthTrack, bool) -> None
        if not self._validate_has_record_clip_tails():
            return None

        self.record_clip_tails_bar_length = scroll_values(
            range(1, 5), self.record_clip_tails_bar_length, go_next
        )
        self.parent.show_message("Record clip tails %s" % BarLengthEnum.int_to_str(self.record_clip_tails_bar_length))

    def _validate_has_record_clip_tails(self):
        # type: (ExternalSynthTrack) -> bool
        if not self.audio_tail_track:
            self.system.show_warning("Please create a clip tail track")
            return False

        return True

    def scroll_presets_or_samples(self, go_next):
        # type: (ExternalSynthTrack, bool) -> Sequence
        """ overridden """
        seq = Sequence()
        if not self.can_change_presets:
            seq.add(self.disable_protected_mode)

        seq.add(partial(super(ExternalSynthTrackActionMixin, self).scroll_presets_or_samples, go_next=go_next))
        return seq.done()

    @property
    def can_change_presets(self):
        # type: (ExternalSynthTrack) -> bool
        if len(self.audio_track.clips) == 0:
            return True
        if not self.protected_mode_active:
            return True
        if not self.instrument.HAS_PROTECTED_MODE:
            return True

        return False

    def disable_protected_mode(self):
        # type: (ExternalSynthTrack) -> Sequence
        seq = Sequence()
        seq.prompt("Disable protected mode ?")
        seq.add(partial(setattr, self, "protected_mode_active", False))
        seq.add(partial(self.parent.show_message, "track protected mode disabled"))
        return seq.done()

    def create_tail_track(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        self.is_folded = False
        return self.audio_track.duplicate()
