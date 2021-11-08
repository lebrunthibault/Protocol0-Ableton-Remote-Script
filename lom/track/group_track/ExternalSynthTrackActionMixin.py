from functools import partial

from typing import TYPE_CHECKING, Optional

from protocol0.devices.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.enums.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.clip.MidiClip import MidiClip
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.utils import find_if

if TYPE_CHECKING:
    from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


# noinspection PyTypeHints
class ExternalSynthTrackActionMixin(object):
    def validate_configuration(self, log=True):
        # type: (ExternalSynthTrack, bool) -> bool
        """ this needs to be deferred because routings are not available on the first tick """
        instrument = find_if(lambda i: isinstance(i, AbstractExternalSynthTrackInstrument), [self.midi_track.instrument,
                                                                                             self.audio_track.instrument])  # type: Optional[AbstractExternalSynthTrackInstrument]
        if not self.midi_track.get_device_from_enum(instrument.EXTERNAL_INSTRUMENT_DEVICE):
            if log:
                self.parent.log_error("Expected to find external instrument device %s in %s" % (
                    instrument.EXTERNAL_INSTRUMENT_DEVICE, self))
            return False
        if not self.audio_track.input_routing_type.attached_object == self.midi_track._track:
            if log:
                self.parent.log_error("The audio track input routing should be its associated midi track : %s" % self)
            return False
        if instrument.AUDIO_INPUT_ROUTING_CHANNEL.label != self.audio_track.input_routing_channel.display_name:
            if log:
                self.parent.log_error("Expected to find audio input routing channel to %s : %s" % (
                    instrument.AUDIO_INPUT_ROUTING_CHANNEL.label, self))
            return False
        return True

    def fix_configuration(self):
        # type: (ExternalSynthTrack) -> None
        instrument = find_if(lambda i: isinstance(i, AbstractExternalSynthTrackInstrument), [self.midi_track.instrument,
                                                                                             self.audio_track.instrument])  # type: Optional[AbstractExternalSynthTrackInstrument]
        if not self.midi_track.get_device_from_enum(instrument.EXTERNAL_INSTRUMENT_DEVICE):
            return

    def arm_track(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        self.base_track.is_folded = False
        self.base_track.mute = False
        seq = Sequence(silent=True)
        seq.add([self.midi_track.arm_track, self.audio_track.arm_track])
        seq.add(partial(setattr, self, "has_monitor_in", False))
        return seq.done()

    def unarm_track(self):
        # type: (ExternalSynthTrack) -> None
        self.has_monitor_in = True

    @property
    def has_monitor_in(self):
        # type: (ExternalSynthTrack) -> bool
        return self.midi_track.mute is True

    @has_monitor_in.setter
    def has_monitor_in(self, has_monitor_in):
        # type: (ExternalSynthTrack, bool) -> None
        self.audio_track.current_monitoring_state = CurrentMonitoringStateEnum.OFF
        if has_monitor_in:
            self.midi_track.current_monitoring_state = CurrentMonitoringStateEnum.IN
            self.midi_track.mute = True
            self.audio_track.mute = False
            if self._external_device:
                self._external_device.mute = True
        else:
            self.midi_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
            self.midi_track.mute = False
            self.audio_track.mute = True
            if self._external_device:
                self._external_device.mute = False
        # noinspection PyUnresolvedReferences
        self.notify_has_monitor_in()

    def switch_monitoring(self):
        # type: (ExternalSynthTrack) -> None
        self.has_monitor_in = not self.has_monitor_in

    def undo_track(self):
        # type: (ExternalSynthTrack) -> None
        for sub_track in self.sub_tracks:
            sub_track.undo_track()

    def session_record_all(self):
        # type: (ExternalSynthTrack) -> Sequence
        seq = Sequence()

        if self.next_empty_clip_slot_index is None:
            return seq.done()

        self.has_monitor_in = False

        midi_clip_slot = self.midi_track.clip_slots[self.next_empty_clip_slot_index]
        audio_clip_slot = self.audio_track.clip_slots[self.next_empty_clip_slot_index]
        self.audio_track.select()
        recording_bar_length = InterfaceState.SELECTED_RECORDING_BAR_LENGTH.int_value
        bar_tail_length = InterfaceState.record_clip_tails_length()

        seq.add([
            partial(midi_clip_slot.record, bar_length=recording_bar_length, bar_tail_length=bar_tail_length),
            partial(audio_clip_slot.record, bar_length=recording_bar_length, bar_tail_length=bar_tail_length)]
        )
        if InterfaceState.SELECTED_RECORDING_BAR_LENGTH == BarLengthEnum.UNLIMITED:
            return seq.done()

        if InterfaceState.RECORD_CLIP_TAILS:
            seq.add(self.song.selected_scene.fire)
        return seq.done()

    def session_record_audio_only(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        midi_clip = self.midi_track.playable_clip
        if not midi_clip:
            self.parent.show_message("No midi clip selected on %s" % self)
            return None
        if midi_clip != self.midi_track.clip_slots[self.song.selected_scene.index].clip:
            self.parent.show_message("Playable clip is not on the selected scene")
            return None
        assert isinstance(midi_clip, MidiClip)

        audio_clip_slot = self.audio_track.clip_slots[midi_clip.index]
        audio_clip = audio_clip_slot.clip

        self.song.metronome = False
        self.has_monitor_in = False

        seq = Sequence()
        if audio_clip:
            seq.add(audio_clip.delete)

        audio_tail_bar_length = audio_clip.tail_bar_length if audio_clip else 0

        # launch the midi clip after the record has started
        seq.add(partial(self.parent.wait, 80, midi_clip.play))

        seq.add(partial(audio_clip_slot.record, bar_length=midi_clip.bar_length, bar_tail_length=audio_tail_bar_length))
        if audio_clip and audio_clip.tail_bar_length:
            loop_start, loop_end = audio_clip.loop_start, audio_clip.loop_end
            seq.add(lambda: setattr(audio_clip_slot.clip, "loop_start", loop_start))
            seq.add(lambda: setattr(audio_clip_slot.clip, "loop_end", loop_end))
        if InterfaceState.RECORD_CLIP_TAILS or audio_tail_bar_length:
            seq.add(self.song.selected_scene.fire)

        return seq.done()

    def arrangement_record_audio_only(self):
        # type: (ExternalSynthTrack) -> Sequence
        self.midi_track.unarm()
        return self.song.global_record()

    def post_session_record(self, record_type):
        # type: (ExternalSynthTrack, RecordTypeEnum) -> None
        super(ExternalSynthTrackActionMixin, self).post_session_record()
        self.has_monitor_in = True
        if self.midi_track.playable_clip and self.audio_track.playable_clip:
            self.audio_track.playable_clip.post_record()
            if record_type == RecordTypeEnum.NORMAL:
                self.midi_track.playable_clip.clip_name.update(base_name="")
                self.audio_track.playable_clip.clip_name.update(base_name="")
                self.midi_track.playable_clip.post_record()
            else:
                self._link_clip_slots()

    def post_arrangement_record(self):
        # type: (ExternalSynthTrack) -> None
        self.midi_track.arm_track()
        super(ExternalSynthTrackActionMixin, self).post_arrangement_record()
        self.has_monitor_in = True

    def delete_playable_clip(self):
        # type: (ExternalSynthTrack) -> Sequence
        """ only midi clip is needed as clips are sync """
        seq = Sequence()
        seq.add(wait=1)
        if self.midi_track.playable_clip:
            seq.add(partial(self.midi_track.playable_clip.delete))
        return seq.done()

    @property
    def can_change_presets(self):
        # type: (ExternalSynthTrack) -> bool
        """ overridden """
        assert self.instrument
        return super(ExternalSynthTrackActionMixin, self).can_change_presets or len(self.audio_track.clips) == 0
