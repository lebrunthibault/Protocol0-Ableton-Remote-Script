from functools import partial

from typing import Optional, Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.components.UtilsManager import UtilsManager
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.errors.Protocol0Warning import Protocol0Warning
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.track_recorder.factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.track_recorder.factory.track_recoder_simple_factory import TrackRecorderSimpleFactory
from protocol0.track_recorder.factory.track_recorder_external_synth_factory import TrackRecorderExternalSynthFactory
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder


class TrackRecorderManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderManager, self).__init__(*a, **k)
        self._audio_effect_rack_cache = {}
        self.recorder = None  # type: Optional[AbstractTrackRecorder]

    def get_track_recorder_factory(self, track):
        # type: (AbstractTrack) -> AbstractTrackRecorderFactory
        if isinstance(track, SimpleTrack):
            return TrackRecorderSimpleFactory(track)
        elif isinstance(track, ExternalSynthTrack):
            return TrackRecorderExternalSynthFactory(track)
        else:
            raise Protocol0Warning("This track is not recordable")

    def record_track(self, track, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        if self.recorder:
            self.parent.log_warning("Cancelling record of %s" % self.recorder)
            self.recorder.cancel_record()
            self.recorder = None
            return None

        recorder_factory = self.get_track_recorder_factory(track)

        # assert there is a scene we can record on
        recording_scene_index = recorder_factory.get_recording_scene_index(record_type)
        if recording_scene_index is None:
            seq = Sequence()
            seq.add(self.song.create_scene)
            seq.add(partial(self.record_track, track, record_type))
            return seq.done()

        bar_length = recorder_factory.get_recording_bar_length(record_type)
        self.recorder = recorder_factory.create_recorder(record_type, recording_scene_index, bar_length)

        seq = Sequence()
        seq.add(partial(self._start_recording, bar_length))
        seq.add(partial(setattr, self, "recorder", None))
        return seq.done()

    def _start_recording(self, bar_length):
        # type: (int) -> Optional[Sequence]
        self.parent.show_message("Starting recording of %s" % UtilsManager.get_legend_from_bar_length(bar_length))

        seq = Sequence()
        seq.add(self.recorder.pre_record)
        seq.add(partial(self.recorder.record, bar_length=bar_length))
        seq.add(self.recorder.post_audio_record)
        seq.add(self.song.selected_scene.fire)
        seq.add(complete_on=self.parent.beatScheduler.bar_ending_listener)
        seq.add(self.recorder.post_record)

        return seq.done()
