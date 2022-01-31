from functools import partial

from typing import Optional

from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.domain.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.lom.track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface
from protocol0.domain.track_recorder.factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.domain.track_recorder.factory.track_recoder_simple_factory import TrackRecorderSimpleFactory
from protocol0.domain.track_recorder.factory.track_recorder_external_synth_factory import \
    TrackRecorderExternalSynthFactory
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.domain.utils import get_length_legend


class TrackRecorderManager(AbstractControlSurfaceComponent):
    def get_track_recorder_factory(self, track):
        # type: (AbstractTrack) -> AbstractTrackRecorderFactory
        if isinstance(track, SimpleTrack):
            return TrackRecorderSimpleFactory(track)
        elif isinstance(track, ExternalSynthTrack):
            return TrackRecorderExternalSynthFactory(track)
        else:
            raise Protocol0Warning("This track is not recordable")

    def cancel_record(self, track, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> None
        self.system.show_warning("Cancelling record")
        recorder_factory = self.get_track_recorder_factory(track)
        bar_length = recorder_factory.get_recording_bar_length(record_type)
        recorder = recorder_factory.create_recorder(record_type, bar_length)
        recorder.set_recording_scene_index(self.song.selected_scene.index)
        self.parent.clear_tasks()
        recorder.cancel_record()
        return None

    def record_track(self, track, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        # assert there is a scene we can record on
        if track.is_recording:
            raise Protocol0Warning("the track is recording")

        recorder_factory = self.get_track_recorder_factory(track)
        recording_scene_index = recorder_factory.get_recording_scene_index(record_type)
        if recording_scene_index is None:
            seq = Sequence()
            seq.add(self.song.create_scene)
            seq.add(partial(self.record_track, track, record_type))
            return seq.done()

        bar_length = recorder_factory.get_recording_bar_length(record_type)
        count_in = recorder_factory.create_count_in(record_type)
        recorder = recorder_factory.create_recorder(record_type, bar_length)
        recorder.set_recording_scene_index(recording_scene_index)

        return self._start_recording(count_in, recorder, bar_length)

    def _start_recording(self, count_in, recorder, bar_length):
        # type: (CountInInterface, AbstractTrackRecorder, int) -> Optional[Sequence]
        self.parent.show_message("Starting recording of %s" % get_length_legend(bar_length))

        seq = Sequence()
        seq.add(recorder.pre_record)
        seq.add(count_in.launch)
        seq.add(partial(recorder.record, bar_length=bar_length))
        seq.add(recorder.post_audio_record)
        seq.add(self.song.selected_scene.fire)
        seq.add(complete_on=self.parent.beatScheduler.bar_ending_listener)
        seq.add(recorder.post_record)
        seq.add(partial(setattr, self, "recorderFactory", None))

        return seq.done()
