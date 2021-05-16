from functools import partial

import Live
from typing import TYPE_CHECKING, Optional

from a_protocol_0.devices.InstrumentMinitaur import InstrumentMinitaur
from a_protocol_0.enums.ColorEnum import ColorEnum
from a_protocol_0.lom.clip.MidiClip import MidiClip
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


# noinspection PyTypeHints
class ExternalSynthTrackActionMixin(object):
    def arm_track(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        self.color = ColorEnum.ARM
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

    def record_all(self):
        # type: (ExternalSynthTrack) -> Sequence
        """ next_empty_clip_slot_index is guaranteed to be not None """
        seq = Sequence()
        assert self.next_empty_clip_slot_index is not None
        midi_clip_slot = self.midi_track.clip_slots[self.next_empty_clip_slot_index]
        audio_clip_slot = self.audio_track.clip_slots[self.next_empty_clip_slot_index]
        self.audio_track.select()
        seq.add([midi_clip_slot.record, audio_clip_slot.record])
        seq.add(self._post_record)
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
        recording_bar_count = int(round((self.midi_track.playable_clip.length + 1) / self.song.signature_denominator))
        audio_clip_slot = self.audio_track.clip_slots[midi_clip.index]
        if audio_clip_slot.clip:
            seq.add(audio_clip_slot.clip.delete)
        seq.add(partial(setattr, midi_clip, "start_marker", 0))
        seq.add(partial(self.parent._wait, 80, midi_clip.play))  # launching the midi clip after the record has started
        seq.add(partial(self.audio_track.clip_slots[midi_clip.index].record, recording_bar_count=recording_bar_count))
        seq.add(self._post_record)
        return seq.done()

    def undo_track(self):
        # type: (ExternalSynthTrack) -> None
        for sub_track in self.sub_tracks:
            sub_track.undo_track()

    def _post_record(self):
        # type: (ExternalSynthTrack) -> None
        super(ExternalSynthTrackActionMixin, self)._post_record()
        self.midi_track.has_monitor_in = self.audio_track.has_monitor_in = False
        self.audio_track.playable_clip.warp_mode = Live.Clip.WarpMode.tones
