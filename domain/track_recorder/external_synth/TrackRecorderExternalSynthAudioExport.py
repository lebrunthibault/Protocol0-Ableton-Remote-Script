from functools import partial

from typing import Any, Optional

from protocol0.domain.lom.clip.ClipNameEnum import ClipNameEnum
from protocol0.domain.shared.backend.Backend import Backend
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

        self.atk_cs = None  # type: Optional[SourceClipSlot]
        self.loop_cs = None  # type: Optional[SourceClipSlot]

    def legend(self, bar_length):
        # type: (int) -> str
        return "audio export %s bars" % str(bar_length)

    def pre_record(self):
        # type: () -> Sequence
        self.atk_cs = SourceClipSlot(
            self.track.audio_track, self.recording_scene_index, ClipNameEnum.ATK.value
        )
        self.loop_cs = SourceClipSlot(
            self.track.audio_tail_track, self.recording_scene_index, ClipNameEnum.LOOP.value
        )

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

    def _focus_main_clip(self):
        # type: () -> Optional[Sequence]
        return None

    def post_record(self, bar_length):
        # type: (int) -> Optional[Sequence]
        seq = Sequence()
        seq.add(partial(super(TrackRecorderExternalSynthAudioExport, self).post_record, bar_length))

        seq.wait(11)

        seq.add(self.atk_cs.post_record)
        seq.add(self.loop_cs.post_record)

        seq.add(partial(self._configure_loop_clip, bar_length))
        seq.add(self._replace_clips)

        return seq.done()

    def _configure_loop_clip(self, bar_length):
        # type: (int) -> None
        if self.loop_cs.clip is not None:
            length = bar_length * SongFacade.signature_numerator()
            self.loop_cs.clip.loop._clip.loop_end = float(length)

    def _replace_clips(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(self.atk_cs.replace_clips)
        seq.add(self.loop_cs.replace_clips)

        clips_replaced_count = len(self.atk_cs.matching_clip_slots) + len(
            self.loop_cs.matching_clip_slots
        )
        seq.add(partial(Backend.client().show_success, "%s clips replaced" % clips_replaced_count))

        return seq.done()
