from functools import partial

from typing import Any, Optional, List

from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudio import (
    TrackRecorderExternalSynthAudio,
)
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthClipSlot import (
    SourceClipSlot,
)
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioExport(TrackRecorderExternalSynthAudio):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderExternalSynthAudioExport, self).__init__(*a, **k)

        self._source_clip_slots = []  # type: List[SourceClipSlot]

    @property
    def loop_cs(self):
        # type: () -> Optional[AudioClipSlot]
        return self._source_clip_slots[1].clip_slot

    @property
    def end_cs(self):
        # type: () -> Optional[AudioClipSlot]
        return self._source_clip_slots[2].clip_slot

    def legend(self, bar_length):
        # type: (int) -> str
        return "audio export %s bars" % str(bar_length)

    def pre_record(self):
        # type: () -> Sequence
        self._source_clip_slots[:] = [
            SourceClipSlot(self.track.audio_track, self.recording_scene_index, "atk"),
            SourceClipSlot(self.track.audio_tail_track, self.recording_scene_index, "loop"),
            SourceClipSlot(self.track.audio_tail_track, self.recording_scene_index + 1, "end"),
        ]  # type: List[SourceClipSlot]

        return super(TrackRecorderExternalSynthAudioExport, self).pre_record()

    def record(self, bar_length):
        # type: (float) -> Sequence
        if (
            self.track.audio_tail_track is None
            or not self.track.audio_tail_track.arm_state.is_armed
        ):
            return super(TrackRecorderExternalSynthAudioExport, self).record(bar_length)

        self.track.audio_tail_track.arm_state.unarm()

        seq = Sequence()
        seq.add(partial(super(TrackRecorderExternalSynthAudioExport, self).record, bar_length))
        seq.add(self.track.audio_track.stop)
        seq.add(self.track.audio_tail_track.arm_state.arm)
        seq.add(partial(super(TrackRecorderExternalSynthAudioExport, self).record, bar_length))

        return seq.done()

    def post_record(self, bar_length):
        # type: (int) -> Optional[Sequence]
        seq = Sequence()
        seq.add(partial(super(TrackRecorderExternalSynthAudioExport, self).post_record, bar_length))

        if self.loop_cs.clip is not None:
            seq.add(partial(self.loop_cs.duplicate_clip_to, self.end_cs))
            seq.add(partial(setattr, self.loop_cs.clip, "bar_length", bar_length))
        seq.wait(11)

        for source_cs in self._source_clip_slots:
            seq.add(source_cs.post_record)

        seq.add(self._replace_clips)

        return seq.done()

    def _replace_clips(self):
        # type: () -> None
        replace_res = map(lambda cs: cs.replace_clips(), self._source_clip_slots)
        clips_replaced_count, clips_count = [sum(x) for x in zip(*replace_res)]

        message = "%s / %s clips replaced" % (clips_replaced_count, clips_count)
        if clips_count == 0:
            Backend.client().show_warning(message)
        elif clips_count == clips_replaced_count:
            Backend.client().show_success(message)
        else:
            Backend.client().show_info(message)
