import itertools
from functools import partial

from typing import TYPE_CHECKING, Optional, cast, Iterator

from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.enums.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.clip.MidiClip import MidiClip
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import prompt

if TYPE_CHECKING:
    from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


# noinspection PyTypeHints
class ExternalSynthTrackActionMixin(object):
    def arm_track(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        self.base_track.is_folded = False
        self.base_track.mute = False
        if self.song.usamo_track:
            self.song.usamo_track.input_routing_track = self.midi_track
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

    def _session_record_all(self):
        # type: (ExternalSynthTrack) -> Sequence
        seq = Sequence()

        if self.next_empty_clip_slot_index is None:
            return seq.done()

        self.has_monitor_in = False

        midi_clip_slot = self.midi_track.clip_slots[self.next_empty_clip_slot_index]
        audio_clip_slot = self.audio_track.clip_slots[self.next_empty_clip_slot_index]
        self.audio_track.select()
        recording_bar_length = InterfaceState.SELECTED_RECORDING_BAR_LENGTH.int_value

        seq.add([
            partial(midi_clip_slot.record, bar_length=recording_bar_length),
            partial(audio_clip_slot.record, bar_length=recording_bar_length)]
        )
        if InterfaceState.SELECTED_RECORDING_BAR_LENGTH == BarLengthEnum.UNLIMITED:
            return seq.done()

        if InterfaceState.RECORD_CLIP_TAILS:
            seq.add(self.song.selected_scene.fire)
        return seq.done()

    def _session_record_audio_only(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        midi_clip = self.midi_track.playable_clip
        if not midi_clip:
            self.parent.show_message("No midi clip selected")
            return None
        if midi_clip != self.midi_track.clip_slots[self.song.selected_scene.index].clip:
            self.parent.show_message("Playable clip is not on the selected scene")
            return None
        assert isinstance(midi_clip, MidiClip)

        audio_clip_slot = self.audio_track.clip_slots[midi_clip.index]
        audio_clip = cast(AudioClip, audio_clip_slot.clip)

        self.song.metronome = False
        self.has_monitor_in = False

        seq = Sequence()
        if audio_clip:
            audio_clip_slot.previous_audio_file_path = audio_clip.file_path
            seq.add(audio_clip.delete)

        seq.add(partial(audio_clip_slot.record, bar_length=midi_clip.bar_length))
        seq.add(partial(self._propagate_new_audio_clip, audio_clip_slot))

        if InterfaceState.RECORD_CLIP_TAILS:
            seq.add(self.song.selected_scene.fire)

        return seq.done()

    def _propagate_new_audio_clip(self, audio_clip_slot):
        # type: (ExternalSynthTrack, ClipSlot) -> None
        source_midi_clip = self.midi_track.clip_slots[audio_clip_slot.index].clip
        source_audio_clip = self.audio_track.clip_slots[audio_clip_slot.index].clip
        if source_midi_clip is None or source_audio_clip is None:
            return None
        duplicate_audio_clips = list(self._get_duplicate_audio_clips(source_midi_clip, source_audio_clip))
        if len(duplicate_audio_clips) == 0:
            return

        seq = Sequence()
        seq.add(
            partial(self.system.prompt, "Propagate to %s audio clips in track ?" % len(duplicate_audio_clips)),
            wait_for_system=True)
        seq.add([partial(source_audio_clip.clip_slot.duplicate_clip_to, clip.clip_slot) for clip in duplicate_audio_clips])
        seq.add(lambda: self.parent.show_message("%s audio clips duplicated" % len(duplicate_audio_clips)))
        seq.done()

    def _get_duplicate_audio_clips(self, source_midi_clip, source_audio_clip):
        # type: (ExternalSynthTrack, MidiClip, AudioClip) -> Iterator[AudioClip]
        source_midi_hash = source_midi_clip.hash()
        source_file_path = source_audio_clip.clip_slot.previous_audio_file_path
        for midi_clip, audio_clip in itertools.izip(self.midi_track.clips, self.audio_track.clips):  # type: (MidiClip, AudioClip)
            if midi_clip == source_midi_clip:
                continue
            if midi_clip.hash() != source_midi_hash:
                continue
            if audio_clip.file_path != source_file_path:
                continue
            yield audio_clip

    def arrangement_record_audio_only(self):
        # type: (ExternalSynthTrack) -> Sequence
        self.midi_track.unarm()
        return self.song.global_record()

    def post_session_record(self, record_type):
        # type: (ExternalSynthTrack, RecordTypeEnum) -> None
        super(ExternalSynthTrackActionMixin, self).post_session_record(update_clip_name=False)
        midi_clip = self.midi_track.playable_clip
        audio_clip = self.audio_track.playable_clip
        if not midi_clip or not audio_clip:
            return None

        audio_clip.post_record()
        if record_type == RecordTypeEnum.NORMAL:
            midi_clip.clip_name.update(base_name="")
            audio_clip.clip_name.update(base_name="")
            midi_clip.post_record()
            midi_clip.select()
            self.parent.navigationManager.focus_main()
        else:
            audio_clip.clip_name.update(base_name=midi_clip.clip_name.base_name)
            self.link_clip_slots()

    def post_arrangement_record(self):
        # type: (ExternalSynthTrack) -> None
        self.midi_track.arm_track()
        super(ExternalSynthTrackActionMixin, self).post_arrangement_record()
        self.has_monitor_in = True

    def delete_playable_clip(self):
        # type: (ExternalSynthTrack) -> Sequence
        """ only midi clip is needed as clips are sync """
        seq = Sequence()
        if self.midi_track.playable_clip:
            seq.add(partial(self.midi_track.playable_clip.delete))
        return seq.done()

    @property
    def can_change_presets(self):
        # type: (ExternalSynthTrack) -> bool
        """ overridden """
        if len(self.audio_track.clips) == 0:
            return True
        if not self.protected_mode_active:
            return True
        else:
            self.disable_protected_mode()
            return False

    @prompt("Disable protected mode ?")
    def disable_protected_mode(self):
        # type: (ExternalSynthTrack) -> None
        self.protected_mode_active = False
        self.parent.show_message("track protected mode disabled")
