from functools import partial

from typing import Any, Optional, List

from protocol0.domain.lom.clip.ClipNameEnum import ClipNameEnum
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudio import (
    TrackRecorderExternalSynthAudio,
)
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthClipSlot import (
    SourceClipSlot,
)
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioExport(TrackRecorderExternalSynthAudio):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderExternalSynthAudioExport, self).__init__(*a, **k)

        self._source_clip_slots = []  # type: List[SourceClipSlot]

    @property
    def atk_cs(self):
        # type: () -> Optional[SourceClipSlot]
        return self._source_clip_slots[0]

    @property
    def loop_cs(self):
        # type: () -> Optional[SourceClipSlot]
        return self._source_clip_slots[1]

    def legend(self, bar_length):
        # type: (int) -> str
        return "audio export %s bars" % str(bar_length)

    def pre_record(self):
        # type: () -> Sequence
        self._source_clip_slots[:] = [
            SourceClipSlot(
                self.track.audio_track, self.recording_scene_index, ClipNameEnum.ATK.value
            ),
            SourceClipSlot(
                self.track.audio_tail_track, self.recording_scene_index, ClipNameEnum.LOOP.value
            ),
        ]  # type: List[SourceClipSlot]

        has_matching_clip = any(
            self.atk_cs.matches_clip(cs) for cs in self.track.audio_track.clip_slots
        )
        if self.track.audio_tail_track is not None:
            has_matching_clip = has_matching_clip or any(
                self.atk_cs.matches_clip(cs) for cs in self.track.audio_tail_track.clip_slots
            )

        if has_matching_clip:
            raise Protocol0Warning("This midi clip was already recorded in this track")

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

        seq.wait(11)

        for source_cs in self._source_clip_slots:
            seq.add(source_cs.post_record)

        seq.add(partial(self._configure_clips, bar_length))
        seq.add(self._replace_clips)

        return seq.done()

    def _configure_clips(self, bar_length):
        # type: (int) -> None
        if self.loop_cs.clip is not None:
            length = bar_length * SongFacade.signature_numerator()
            self.loop_cs.clip.loop._clip.loop_end = length

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
