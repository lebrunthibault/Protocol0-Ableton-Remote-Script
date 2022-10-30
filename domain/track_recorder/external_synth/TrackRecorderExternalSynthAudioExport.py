from functools import partial

from typing import Any, Optional, Tuple

from protocol0.domain.lom.clip.ClipSampleService import ClipToReplace
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.external_synth.ClipToReplaceDetectedEvent import (
    ClipToReplaceDetectedEvent,
)
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudio import (
    TrackRecorderExternalSynthAudio,
)
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioExport(TrackRecorderExternalSynthAudio):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderExternalSynthAudioExport, self).__init__(*a, **k)
        self._atk_file_path = None  # type: Optional[str]
        self._loop_file_path = None  # type: Optional[str]
        self._end_file_path = None  # type: Optional[str]

    @property
    def atk_cs(self):
        # type: () -> AudioClipSlot
        return self.track.audio_track.clip_slots[self.recording_scene_index]

    @property
    def loop_cs(self):
        # type: () -> Optional[AudioClipSlot]
        if self.track.audio_tail_track is None:
            return None
        else:
            return self.track.audio_tail_track.clip_slots[self.recording_scene_index]

    @property
    def end_cs(self):
        # type: () -> Optional[AudioClipSlot]
        if (
                self.track.audio_tail_track is None
                or len(SongFacade.scenes()) <= self.recording_scene_index + 1
        ):
            return None
        else:
            return self.track.audio_tail_track.clip_slots[self.recording_scene_index + 1]

    def legend(self, bar_length):
        # type: (int) -> str
        return "audio export %s bars" % str(bar_length)

    def pre_record(self):
        # type: () -> Sequence
        if self.atk_cs.clip is not None:
            self._atk_file_path = self.atk_cs.clip.file_path

        if self.track.audio_tail_track is not None:
            if self.loop_cs.clip is not None:
                self._loop_file_path = self.loop_cs.clip.file_path

            if self.end_cs is not None and self.end_cs.clip is not None:
                self._end_file_path = self.end_cs.clip.file_path
                self.end_cs.delete_clip()

        return super(TrackRecorderExternalSynthAudioExport, self).pre_record()

    def record(self, bar_length):
        # type: (float) -> Sequence
        if self.track.audio_tail_track is None:
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

        if self.track.audio_tail_track is not None:
            audio_tail_clip = self.track.audio_tail_track.clip_slots[
                self.recording_scene_index
            ].clip
            # in case of manual stop
            if audio_tail_clip is not None:
                seq.add(partial(setattr, audio_tail_clip, "muted", False))
        seq.add(partial(self._rename_clips, bar_length))
        seq.add(self._mark_clips)
        return seq.done()

    def _rename_clips(self, bar_length):
        # type: (int) -> Optional[Sequence]
        if self.track.audio_tail_track is None:
            self.track.audio_track.clip_slots[self.recording_scene_index].clip.clip_name.update(
                "loop"
            )
            return None

        self.atk_cs.clip.clip_name.update("atk")
        self.loop_cs.clip.clip_name.update("loop")

        seq = Sequence()
        if self.end_cs is not None:
            seq.add(partial(self.loop_cs.duplicate_clip_to, self.end_cs))
            seq.add(lambda: self.end_cs.clip.clip_name.update("end"))
        seq.add(partial(setattr, self.loop_cs.clip, "bar_length", bar_length))

        return seq.done()

    def _mark_clips(self):
        # type: () -> None
        clips_replaced_count = 0
        clips_count = 0

        for (source_cs, file_path) in [
            (self.atk_cs, self._atk_file_path),
            (self.loop_cs, self._loop_file_path),
            (self.end_cs, self._end_file_path),
        ]:
            if file_path is None or source_cs is None:
                continue

            replaced, total = self._replace_clips(source_cs, file_path)
            clips_replaced_count += replaced
            clips_count += total

        message = "%s / %s clips replaced" % (clips_replaced_count, clips_count)
        if clips_count == 0:
            Backend.client().show_warning(message)
        elif clips_count == clips_replaced_count:
            Backend.client().show_success(message)
        else:
            Backend.client().show_info(message)

    def _replace_clips(self, source_cs, file_path):
        # type: (AudioClipSlot, str) -> Tuple[int, int]
        clips_replaced_count = 0
        clips_count = 0

        for track in SongFacade.simple_tracks(SimpleAudioTrack):
            for clip_slot in track.clip_slots:
                clip = clip_slot.clip

                # dissociate between loop and end on clip length
                if clip is not None and clip.file_path == file_path and clip.length == source_cs.clip.length:
                    automated_params = clip.automation.get_automated_parameters(
                        track.devices.parameters
                    )

                    clips_count += 1

                    # duplicate when no automation else manual action is needed
                    if len(automated_params) == 0:
                        clips_replaced_count += 1
                        clip_slot.replace_clip(source_cs)
                    else:
                        clip_to_replace = ClipToReplace(track, clip_slot, source_cs.clip.file_path)
                        DomainEventBus.emit(ClipToReplaceDetectedEvent(clip_to_replace))

        return clips_replaced_count, clips_count
