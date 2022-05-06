import itertools
from functools import partial

from typing import Iterator, Optional

from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.TrackRecorderDecorator import TrackRecorderDecorator
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderPropagateNewAudioClipDecorator(TrackRecorderDecorator):
    @property
    def track(self):
        # type: (AbstractTrackRecorder) -> ExternalSynthTrack
        # noinspection PyTypeChecker
        return self._track

    def post_record(self, bar_length):
        # type: (int) -> None
        super(TrackRecorderPropagateNewAudioClipDecorator, self).post_record(bar_length)
        self._propagate_new_audio_clip()

    def _propagate_new_audio_clip(self):
        # type: () -> Optional[Sequence]
        audio_cs = self.track.audio_track.clip_slots[self.recording_scene_index]
        source_midi_cs = self.track.midi_track.clip_slots[audio_cs.index]
        source_midi_clip = source_midi_cs.clip
        source_audio_cs = self.track.audio_track.clip_slots[audio_cs.index]
        source_audio_clip = source_audio_cs.clip
        if source_midi_clip is None or source_audio_cs.clip is None:
            return None

        duplicate_audio_clip_slots = list(self._get_duplicate_audio_clip_slots(source_midi_cs, source_audio_cs))
        if len(duplicate_audio_clip_slots) == 0:
            return None

        seq = Sequence()
        seq.prompt("Propagate to %s audio clips in track ?" % len(duplicate_audio_clip_slots))

        seq.add([partial(source_audio_cs.duplicate_clip_to, clip) for clip in duplicate_audio_clip_slots])

        duplicate_midi_clips = [self.track.midi_track.clip_slots[cs.index].clip for cs in duplicate_audio_clip_slots]
        seq.add([partial(clip.clip_name.update, base_name=source_audio_clip.clip_name.base_name) for clip in
                 duplicate_midi_clips])

        if self.track.audio_tail_track:
            source_tail_cs = self.track.audio_tail_track.clip_slots[source_audio_cs.index]
            duplicate_audio_tail_clip_slots = [self.track.audio_tail_track.clip_slots[cs.index] for cs in
                                               duplicate_audio_clip_slots]
            seq.add([partial(source_tail_cs.duplicate_clip_to, cs) for cs in duplicate_audio_tail_clip_slots])

        seq.add(lambda: StatusBar.show_message("%s audio clips duplicated" % len(duplicate_audio_clip_slots)))
        return seq.done()

    def _get_duplicate_audio_clip_slots(self, source_midi_cs, source_audio_cs):
        # type: (MidiClipSlot, AudioClipSlot) -> Iterator[AudioClipSlot]
        source_midi_hash = source_midi_cs.clip.hash()
        source_file_path = source_audio_cs.previous_audio_file_path
        for midi_cs, audio_cs in itertools.izip(self.track.midi_track.clip_slots,
                                                self.track.audio_track.clip_slots):  # type: (MidiClipSlot, AudioClipSlot)
            if not midi_cs.clip or not audio_cs.clip:
                continue
            if midi_cs == source_midi_cs:
                continue
            if midi_cs.clip.hash() != source_midi_hash:
                continue
            if audio_cs.clip.file_path != source_file_path:
                continue
            yield audio_cs
