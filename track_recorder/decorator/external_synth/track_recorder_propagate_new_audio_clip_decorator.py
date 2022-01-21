import itertools
from functools import partial

from typing import Iterator

from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.clip.MidiClip import MidiClip
from protocol0.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.track_recorder.decorator.external_synth.abstract_track_recorder_external_synth_decorator import \
    AbstractTrackRecorderExternalSynthDecorator
from protocol0.sequence.Sequence import Sequence


class TrackRecorderPropagateNewAudioClipDecorator(AbstractTrackRecorderExternalSynthDecorator):
    def record(self, bar_length):
        # type: (int) -> Sequence
        seq = Sequence()
        seq.add(partial(super(TrackRecorderPropagateNewAudioClipDecorator, self).record, bar_length))
        seq.add(self._propagate_new_audio_clip)
        return seq.done()

    def _propagate_new_audio_clip(self, recording_scene_index):
        # type: (int) -> None
        audio_clip_slot = self.track.audio_track.clip_slots[recording_scene_index]
        source_midi_clip = self.track.midi_track.clip_slots[audio_clip_slot.index].clip
        source_audio_clip = self.track.audio_track.clip_slots[audio_clip_slot.index].clip
        if source_midi_clip is None or source_audio_clip is None:
            return None

        source_cs = source_audio_clip.clip_slot

        duplicate_audio_clip_slots = list(self._get_duplicate_audio_clip_slots(source_midi_clip, source_audio_clip))
        if len(duplicate_audio_clip_slots) == 0:
            return

        seq = Sequence()
        seq.prompt("Propagate to %s audio clips in track ?" % len(duplicate_audio_clip_slots))

        seq.add([partial(source_cs.duplicate_clip_to, clip) for clip in duplicate_audio_clip_slots])

        duplicate_midi_clips = [self.track.midi_track.clip_slots[cs.index].clip for cs in duplicate_audio_clip_slots]
        seq.add([partial(clip.clip_name.update, base_name=source_audio_clip.clip_name.base_name) for clip in
                 duplicate_midi_clips])

        if self.track.audio_tail_track:
            source_tail_cs = self.track.audio_tail_track.clip_slots[source_cs.index]
            duplicate_audio_tail_clip_slots = [self.track.audio_tail_track.clip_slots[cs.index] for cs in
                                               duplicate_audio_clip_slots]
            seq.add([partial(source_tail_cs.duplicate_clip_to, cs) for cs in duplicate_audio_tail_clip_slots])

        seq.add(lambda: self.parent.show_message("%s audio clips duplicated" % len(duplicate_audio_clip_slots)))
        seq.done()

    def _get_duplicate_audio_clip_slots(self, source_midi_clip, source_audio_clip):
        # type: (MidiClip, AudioClip) -> Iterator[AudioClipSlot]
        source_midi_hash = source_midi_clip.hash()
        source_file_path = source_audio_clip.clip_slot.previous_audio_file_path
        for midi_clip, audio_clip in itertools.izip(self.track.midi_track.clips,
                                                    self.track.audio_track.clips):  # type: (MidiClip, AudioClip)
            if midi_clip == source_midi_clip:
                continue
            if midi_clip.hash() != source_midi_hash:
                continue
            if audio_clip.file_path != source_file_path:
                continue
            yield audio_clip.clip_slot
