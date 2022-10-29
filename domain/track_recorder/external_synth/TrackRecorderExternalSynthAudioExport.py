from functools import partial

from typing import Any, Optional, cast

from protocol0.domain.lom.clip.ClipSampleService import ClipToReplace
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.external_synth.ClipToReplaceDetectedEvent import \
    ClipToReplaceDetectedEvent
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudio import (
    TrackRecorderExternalSynthAudio,
)
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioExport(TrackRecorderExternalSynthAudio):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderExternalSynthAudioExport, self).__init__(*a, **k)
        self._audio_file_path = None  # type: Optional[str]
        self._audio_tail_file_path = None  # type: Optional[str]

    def pre_record(self):
        # type: () -> Sequence
        audio_clip = self.track.audio_track.clip_slots[self.recording_scene_index].clip
        if audio_clip is not None:
            self._audio_file_path = audio_clip.file_path

        audio_tail_clip = self.track.audio_tail_track.clip_slots[self.recording_scene_index].clip
        if audio_tail_clip is not None:
            self._audio_tail_file_path = audio_tail_clip.file_path

        return super(TrackRecorderExternalSynthAudioExport, self).pre_record()

    def record(self, bar_length):
        # type: (float) -> Sequence
        self.track.audio_tail_track.arm_state.unarm()
        seq = Sequence()
        seq.add(partial(super(TrackRecorderExternalSynthAudioExport, self).record, bar_length))
        seq.add(self.track.audio_track.stop)
        seq.add(self.track.audio_tail_track.arm_state.arm)
        seq.add(partial(super(TrackRecorderExternalSynthAudioExport, self).record, bar_length))

        return seq.done()

    def legend(self, bar_length):
        # type: (int) -> str
        return "audio export %s bars" % str(bar_length)

    def post_record(self, bar_length):
        # type: (int) -> Optional[Sequence]
        super(TrackRecorderExternalSynthAudioExport, self).post_record(bar_length)
        audio_tail_clip = self.track.audio_tail_track.clip_slots[self.recording_scene_index].clip
        seq = Sequence()
        seq.wait(11)
        seq.add(partial(setattr, audio_tail_clip, "muted", False))
        seq.add(self._rename_clips)
        seq.add(self._mark_clips)
        return seq.done()

    def _rename_clips(self):
        # type: () -> None
        self.track.audio_track.clip_slots[self.recording_scene_index].clip.clip_name.update("atk")
        self.track.audio_tail_track.clip_slots[self.recording_scene_index].clip.clip_name.update(
            "loop"
        )

    def _mark_clips(self):
        # type: () -> None
        for (source_track, file_path) in [
            (self.track.audio_track, self._audio_file_path),
            (self.track.audio_tail_track, self._audio_tail_file_path),
        ]:
            self._replace_clips(cast(SimpleAudioTrack, source_track), file_path)

    def _replace_clips(self, source_track, file_path):
        # type: (SimpleAudioTrack, Optional[str]) -> None
        if file_path is None:
            return

        audio_tracks = [
            track for track in SongFacade.simple_tracks() if isinstance(track, SimpleAudioTrack)
        ]

        source_cs = source_track.clip_slots[self.recording_scene_index]

        for track in audio_tracks:
            for clip_slot in track.clip_slots:
                if clip_slot.clip is not None and clip_slot.clip.file_path == file_path:
                    automated_params = clip_slot.clip.automation.get_automated_parameters(
                        track.devices.parameters
                    )

                    # duplicate when no automation else manual action is needed
                    if len(automated_params) == 0:
                        Logger.info("Replacing %s" % clip_slot.clip)
                        source_cs.duplicate_clip_to(clip_slot)
                    else:
                        clip_to_replace = ClipToReplace(track, clip_slot, source_cs.clip.file_path)
                        DomainEventBus.emit(ClipToReplaceDetectedEvent(clip_to_replace))
