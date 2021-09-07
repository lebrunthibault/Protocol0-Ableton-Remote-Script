from functools import partial

from typing import TYPE_CHECKING, Optional

import Live
from protocol0.devices.InstrumentMinitaur import InstrumentMinitaur
from protocol0.lom.clip.MidiClip import MidiClip
from protocol0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


# noinspection PyTypeHints
class ExternalSynthTrackActionMixin(object):
    def arm_track(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        self.base_track.is_folded = False
        self.midi_track.has_monitor_in = False
        self.audio_track.has_monitor_in = True
        seq = Sequence(silent=True)
        seq.add([self.midi_track.arm_track, self.audio_track.arm_track])
        return seq.done()

    def unarm_track(self):
        # type: (ExternalSynthTrack) -> None
        self.midi_track.has_monitor_in = self.audio_track.has_monitor_in = False
        if isinstance(self.instrument, InstrumentMinitaur):
            # needed when we have multiple minitaur tracks so that other midi clips are not sent to minitaur
            self.midi_track.has_monitor_in = True

    def switch_monitoring(self):
        # type: (ExternalSynthTrack) -> None
        if self.midi_track.has_monitor_in and self.audio_track.has_monitor_in:
            self.midi_track.has_monitor_in = self.audio_track.has_monitor_in = False
        elif self.audio_track.has_monitor_in:
            self.midi_track.has_monitor_in = True
        else:
            self.audio_track.has_monitor_in = True

    def undo_track(self):
        # type: (ExternalSynthTrack) -> None
        for sub_track in self.sub_tracks:
            sub_track.undo_track()

    def record_all(self):
        # type: (ExternalSynthTrack) -> Sequence
        """ next_empty_clip_slot_index is guaranteed to be not None """
        seq = Sequence()
        assert self.next_empty_clip_slot_index is not None
        midi_clip_slot = self.midi_track.clip_slots[self.next_empty_clip_slot_index]
        audio_clip_slot = self.audio_track.clip_slots[self.next_empty_clip_slot_index]
        self.audio_track.select()
        seq.add([midi_clip_slot.record, audio_clip_slot.record])
        return seq.done()

    def record_audio_only(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        midi_clip = self.midi_track.playable_clip
        if not midi_clip:
            self.parent.show_message("No midi clip selected")
            return None
        assert isinstance(midi_clip, MidiClip)

        self.song.metronome = False

        seq = Sequence()
        recording_bar_count = int(round((self.midi_track.playable_clip.length + 1) / self.song.signature_numerator))
        audio_clip_slot = self.audio_track.clip_slots[midi_clip.index]
        if audio_clip_slot.clip:
            try:
                seq.add(self._clip_slot_synchronizers[audio_clip_slot.index].disconnect)
            except (IndexError, AttributeError):
                pass
            seq.add(audio_clip_slot.clip.delete)
        seq.add(partial(setattr, midi_clip, "start_marker", 0))
        seq.add(partial(self.parent.wait, 80, midi_clip.play))  # launching the midi clip after the record has started
        seq.add(partial(self.audio_track.clip_slots[midi_clip.index].record, recording_bar_count=recording_bar_count))
        return seq.done()

    def post_record(self):
        # type: (ExternalSynthTrack) -> None
        super(ExternalSynthTrackActionMixin, self).post_record()
        self.midi_track.has_monitor_in = self.audio_track.has_monitor_in = False
        if self.midi_track.playable_clip and self.audio_track.playable_clip:
            self.midi_track.playable_clip.quantize()
            self.audio_track.playable_clip.warp_mode = Live.Clip.WarpMode.tones

    def delete_playable_clip(self):
        # type: (ExternalSynthTrack) -> Sequence
        """ only midi clip is needed as clips are sync """
        seq = Sequence()
        if self.midi_track.playable_clip:
            seq.add(self.midi_track.playable_clip.delete)
        return seq.done()

    @property
    def can_change_presets(self):
        # type: (ExternalSynthTrack) -> bool
        """ overridden """
        assert self.instrument
        return super(ExternalSynthTrackActionMixin, self).can_change_presets or len(self.audio_track.clips) == 0
