from functools import partial

from typing import Optional, TYPE_CHECKING

from protocol0.domain.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.System import System
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import get_length_legend
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface
from protocol0.domain.track_recorder.factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.domain.track_recorder.factory.track_recoder_simple_factory import TrackRecorderSimpleFactory
from protocol0.domain.track_recorder.factory.track_recorder_external_synth_factory import \
    TrackRecorderExternalSynthFactory
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.StatusBar import StatusBar

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class TrackRecorderManager(object):
    def __init__(self, song):
        # type: (Song) -> None
        self._song = song

    def get_track_recorder_factory(self, track):
        # type: (AbstractTrack) -> AbstractTrackRecorderFactory
        if isinstance(track, SimpleTrack):
            return TrackRecorderSimpleFactory(track, self._song)
        elif isinstance(track, ExternalSynthTrack):
            return TrackRecorderExternalSynthFactory(track, self._song)
        else:
            raise Protocol0Warning("This track is not recordable")

    def cancel_record(self, track, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> None
        System.client().show_warning("Cancelling record")
        recorder_factory = self.get_track_recorder_factory(track)
        bar_length = recorder_factory.get_recording_bar_length(record_type)
        recorder = recorder_factory.create_recorder(record_type, bar_length)
        recorder.set_recording_scene_index(SongFacade.selected_scene().index)
        Scheduler.clear()
        recorder.cancel_record()
        return None

    def record_track(self, track, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        # assert there is a scene we can record on
        if track.is_recording:
            raise Protocol0Warning("the track is recording")

        recorder_factory = self.get_track_recorder_factory(track)
        Logger.log_dev(recorder_factory)
        recording_scene_index = recorder_factory.get_recording_scene_index(record_type)
        if recording_scene_index is None:
            seq = Sequence()
            seq.add(self._song.create_scene)
            seq.add(partial(self.record_track, track, record_type))
            return seq.done()

        bar_length = recorder_factory.get_recording_bar_length(record_type)
        count_in = recorder_factory.create_count_in(record_type)
        recorder = recorder_factory.create_recorder(record_type, bar_length)
        Logger.log_dev(recorder)
        recorder.set_recording_scene_index(recording_scene_index)

        return self._start_recording(count_in, recorder, bar_length)

    def _start_recording(self, count_in, recorder, bar_length):
        # type: (CountInInterface, AbstractTrackRecorder, int) -> Optional[Sequence]
        StatusBar.show_message("Starting recording of %s" % get_length_legend(bar_length))

        seq = Sequence()
        seq.add(recorder.pre_record)
        seq.add(count_in.launch)
        seq.add(partial(recorder.record, bar_length=bar_length))
        seq.add(recorder.post_audio_record)
        seq.add(SongFacade.selected_scene().fire)
        seq.add(wait_for_event=BarEndingEvent)
        seq.add(recorder.post_record)
        seq.add(partial(setattr, self, "recorderFactory", None))

        return seq.done()
