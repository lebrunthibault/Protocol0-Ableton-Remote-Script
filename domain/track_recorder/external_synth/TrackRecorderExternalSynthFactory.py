from typing import Optional, Any, cast, Type

from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.AbstractTrackRecorderFactory import (
    AbstractTrackRecorderFactory,
)
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.external_synth.decorator.TrackRecorderClipTailDecorator import (
    TrackRecorderClipTailDecorator,
)
from protocol0.shared.SongFacade import SongFacade


class TrackRecorderExternalSynthFactory(AbstractTrackRecorderFactory):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderExternalSynthFactory, self).__init__(*a, **k)
        self.track = cast(ExternalSynthTrack, self.track)

    def create_recorder(self, record_type):
        # type: (RecordTypeEnum) -> AbstractTrackRecorder
        recorder = super(TrackRecorderExternalSynthFactory, self).create_recorder(record_type)

        if self.track.audio_tail_track is not None:
            if record_type.record_tail:
                recorder = TrackRecorderClipTailDecorator(
                    recorder, self._playback_component, self._recording_component
                )

        return recorder

    def _get_recorder_class(self, record_type):
        # type: (RecordTypeEnum) -> Type[AbstractTrackRecorder]
        return record_type.recorder_class

    def get_recording_scene_index(self, record_type):
        # type: (RecordTypeEnum) -> Optional[int]
        if record_type.is_normal_recording:
            for i in range(SongFacade.selected_scene().index, len(SongFacade.scenes())):
                if (
                    not self.track.midi_track.clip_slots[i].clip
                    and not self.track.audio_track.clip_slots[i].clip
                ):
                    return i

            return None
        else:
            if not self.track.midi_track.selected_clip_slot.clip:
                raise Protocol0Warning("No midi clip selected")
            return SongFacade.selected_scene().index

    def get_recording_bar_length(self, record_type):
        # type: (RecordTypeEnum) -> int
        if record_type == RecordTypeEnum.MIDI:
            return self._recording_bar_length
        elif record_type == RecordTypeEnum.MIDI_UNLIMITED:
            return 0
        elif record_type.use_midi_clip_length:
            midi_clip = self.track.midi_track.selected_clip_slot.clip
            return midi_clip.bar_length
        else:
            raise Protocol0Warning("Unmatched record type %s" % record_type)
