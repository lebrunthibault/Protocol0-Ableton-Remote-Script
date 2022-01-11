import itertools
from functools import partial

from typing import TYPE_CHECKING, Optional, cast, Iterator

from protocol0.components.TrackDataManager import save_track_data
from protocol0.components.UtilsManager import UtilsManager
from protocol0.config import Config
from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.enums.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.enums.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.clip.MidiClip import MidiClip
from protocol0.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.lom.clip_slot.AudioTailClipSlot import AudioTailClipSlot
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.lom.clip_slot.MidiClipSlot import MidiClipSlot
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
                self._external_device.toggle_off()
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
                self._external_device.toggle_on()

    def switch_monitoring(self):
        # type: (ExternalSynthTrack) -> None
        self.has_monitor_in = not self.has_monitor_in

    def _pre_session_record(self, record_type):
        # type: (ExternalSynthTrack, RecordTypeEnum) -> Optional[Sequence]
        """ restart audio to get a count in and recfix"""
        self.midi_track.select()
        self.parent.navigationManager.show_device_view()
        self.parent.defer(self.system.show_plugins)

        return super(ExternalSynthTrackActionMixin, self)._pre_session_record(record_type=record_type)

    def _session_record_all(self):
        # type: (ExternalSynthTrack) -> Sequence
        seq = Sequence()

        if self.next_empty_clip_slot_index is None:
            return seq.done()

        self.has_monitor_in = False

        midi_clip_slot = self.midi_track.clip_slots[self.next_empty_clip_slot_index]
        audio_clip_slot = self.audio_track.clip_slots[self.next_empty_clip_slot_index]
        recording_bar_length = InterfaceState.SELECTED_RECORDING_BAR_LENGTH.int_value

        record_step = [
            partial(midi_clip_slot.record, bar_length=recording_bar_length),
            partial(audio_clip_slot.record, bar_length=recording_bar_length),
        ]

        if self.record_clip_tails:
            audio_tail_clip_slot = self.audio_tail_track.clip_slots[self.next_empty_clip_slot_index]
            record_step.append(partial(audio_tail_clip_slot.record, bar_length=recording_bar_length + 1))
            if recording_bar_length:  # and not unlimited
                self._stop_midi_input_to_record_clip_tail(midi_clip_slot=midi_clip_slot,
                                                          bar_length=recording_bar_length)

        seq.add(record_step)

        return seq.done()

    def _session_record_audio_only(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        midi_clip = self.midi_track.playable_clip
        if not midi_clip:
            self.parent.show_message("No midi clip selected")
            return None

        self.song.metronome = False
        self.has_monitor_in = False

        audio_clip_slot = self.audio_track.clip_slots[midi_clip.index]
        audio_clip = cast(AudioClip, audio_clip_slot.clip)

        seq = Sequence()
        if audio_clip:
            audio_clip_slot.previous_audio_file_path = audio_clip.file_path
            seq.add(audio_clip.delete)
        seq.add(audio_clip_slot.add_stop_button)

        audio_tail_clip_slot = None  # type: Optional[AudioTailClipSlot]
        if self.audio_tail_track:
            audio_tail_clip_slot = self.audio_tail_track.clip_slots[midi_clip.index]
            if audio_tail_clip_slot.clip:
                seq.add(audio_tail_clip_slot.clip.delete)
            seq.add(audio_tail_clip_slot.add_stop_button)

            if self.record_clip_tails:
                self._stop_midi_input_to_record_clip_tail(midi_clip_slot=midi_clip.clip_slot,
                                                          bar_length=midi_clip.bar_length)

        clip_slots = [audio_clip_slot] + [audio_tail_clip_slot] if audio_tail_clip_slot else []
        seq.add([cs.add_stop_button for cs in clip_slots])

        bar_length = midi_clip.bar_length
        self.parent.show_message(UtilsManager.get_recording_length_legend(bar_length, self.record_clip_tails,
                                                                          self.record_clip_tails_bar_length))

        seq.add(self.song.stop_playing)
        seq.add(partial(self.stop, immediate=True))
        seq.add(wait=1)
        seq.add(partial(setattr, self.song, "session_record", True))
        seq.add(wait_bars=bar_length)
        if self.record_clip_tails:
            seq.add(midi_clip.stop)
            seq.add(lambda: audio_clip_slot.clip.stop())
            seq.add(lambda: audio_clip_slot.clip.post_record())
            seq.add(wait_beats=2)
            seq.add(self.system.hide_plugins)
            seq.add(midi_clip.select)
            seq.add(wait_beats=2)
            seq.add(self.song.selected_scene.fire)
        seq.add(partial(setattr, self.song, "session_record", False))

        if self.record_clip_tails:
            seq.add(wait_beats=1)  # so that end_marker is computed correctly
            seq.add(lambda: audio_tail_clip_slot.clip.post_record())

        seq.add(partial(self._propagate_new_audio_clip, audio_clip_slot))

        return seq.done()

    def _stop_midi_input_to_record_clip_tail(self, midi_clip_slot, bar_length):
        # type: (ExternalSynthTrack, MidiClipSlot, int) -> Sequence
        """ Just before the very end of the midi clip we temporarily disable midi input and stop the midi clip """
        seq = Sequence()
        if not midi_clip_slot.clip:
            seq.add(complete_on=midi_clip_slot._has_clip_listener)
        seq.add(wait_beats=(bar_length * self.song.signature_numerator) - 0.1)
        input_routing_type = self.midi_track.input_routing_type
        seq.add(partial(setattr, self.midi_track, "input_routing_type", InputRoutingTypeEnum.NO_INPUT))
        seq.add(lambda: midi_clip_slot.clip.stop())
        seq.add(complete_on=lambda: midi_clip_slot.clip._playing_status_listener)
        seq.add(self.song.selected_scene.fire)
        seq.add(wait_bars=self.record_clip_tails_bar_length)
        seq.add(partial(setattr, self.midi_track, "input_routing_type", input_routing_type))
        return seq.done()

    def _propagate_new_audio_clip(self, audio_clip_slot):
        # type: (ExternalSynthTrack, ClipSlot) -> None
        source_midi_clip = self.midi_track.clip_slots[audio_clip_slot.index].clip
        source_audio_clip = self.audio_track.clip_slots[audio_clip_slot.index].clip
        if source_midi_clip is None or source_audio_clip is None:
            return None

        source_cs = source_audio_clip.clip_slot

        duplicate_audio_clip_slots = list(self._get_duplicate_audio_clip_slots(source_midi_clip, source_audio_clip))
        if len(duplicate_audio_clip_slots) == 0:
            return

        seq = Sequence()
        seq.prompt("Propagate to %s audio clips in track ?" % len(duplicate_audio_clip_slots))

        seq.add([partial(source_cs.duplicate_clip_to, clip) for clip in duplicate_audio_clip_slots])

        duplicate_midi_clips = [self.midi_track.clip_slots[cs.index].clip for cs in duplicate_audio_clip_slots]
        seq.add([partial(clip.clip_name.update, base_name=source_audio_clip.clip_name.base_name) for clip in
                 duplicate_midi_clips])

        if self.audio_tail_track:
            source_tail_cs = self.audio_tail_track.clip_slots[source_cs.index]
            duplicate_audio_tail_clip_slots = [self.audio_tail_track.clip_slots[cs.index] for cs in
                                               duplicate_audio_clip_slots]
            seq.add([partial(source_tail_cs.duplicate_clip_to, cs) for cs in duplicate_audio_tail_clip_slots])

        seq.add(lambda: self.parent.show_message("%s audio clips duplicated" % len(duplicate_audio_clip_slots)))
        seq.done()

    def _get_duplicate_audio_clip_slots(self, source_midi_clip, source_audio_clip):
        # type: (ExternalSynthTrack, MidiClip, AudioClip) -> Iterator[AudioClipSlot]
        source_midi_hash = source_midi_clip.hash()
        source_file_path = source_audio_clip.clip_slot.previous_audio_file_path
        for midi_clip, audio_clip in itertools.izip(self.midi_track.clips,
                                                    self.audio_track.clips):  # type: (MidiClip, AudioClip)
            if midi_clip == source_midi_clip:
                continue
            if midi_clip.hash() != source_midi_hash:
                continue
            if audio_clip.file_path != source_file_path:
                continue
            yield audio_clip.clip_slot

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

    def arrangement_record_audio_only(self):
        # type: (ExternalSynthTrack) -> Sequence
        self.midi_track.unarm()
        return self.song.global_record()

    def post_session_record(self, record_type):
        # type: (ExternalSynthTrack, RecordTypeEnum) -> None
        super(ExternalSynthTrackActionMixin, self).post_session_record()

        self.instrument.activate_editor_automation()
        self.system.hide_plugins()
        self.parent.defer(self.song.re_enable_automation)

        midi_clip = self.midi_track.playable_clip
        audio_clip = self.audio_track.playable_clip
        if not midi_clip or not audio_clip:
            return None

        if record_type == RecordTypeEnum.AUDIO_ONLY:
            audio_clip.clip_name.update(base_name=midi_clip.clip_name.base_name)

        midi_clip.select()
        midi_clip.show_loop()
        self.parent.navigationManager.focus_main()

    def post_arrangement_record(self):
        # type: (ExternalSynthTrack) -> None
        self.midi_track.arm_track()
        super(ExternalSynthTrackActionMixin, self).post_arrangement_record()
        self.has_monitor_in = True

    def delete_playable_clip(self):
        # type: (ExternalSynthTrack) -> Sequence
        """ only midi clip is needed as clips are sync """
        seq = Sequence()
        if Config.CURRENT_RECORD_TYPE == RecordTypeEnum.NORMAL:
            seq.add(partial(self.midi_track.delete_playable_clip))
        else:
            seq.add(partial(self.audio_track.delete_playable_clip))
            seq.add(partial(self.audio_tail_track.delete_playable_clip))
        return seq.done()

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
        if self.audio_tail_track:
            return None

        self.is_folded = False

        return self.audio_track.duplicate()
