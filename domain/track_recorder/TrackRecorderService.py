from functools import partial

from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.System import System
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import scroll_values
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.RecordingBarLengthEnum import RecordingBarLengthEnum
from protocol0.domain.track_recorder.SelectedRecordingBarLengthUpdatedEvent import \
    SelectedRecordingBarLengthUpdatedEvent
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface
from protocol0.domain.track_recorder.factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.domain.track_recorder.factory.track_recoder_simple_factory import TrackRecorderSimpleFactory
from protocol0.domain.track_recorder.factory.track_recorder_external_synth_factory import \
    TrackRecorderExternalSynthFactory
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class TrackRecorderService(object):
    def __init__(self, song):
        # type: (Song) -> None
        self._song = song
        self.selected_recording_bar_length = RecordingBarLengthEnum.UNLIMITED
        self._recorder = None  # type: Optional[AbstractTrackRecorder]

    def scroll_recording_time(self, go_next):
        # type: (bool) -> None
        self.selected_recording_bar_length = scroll_values(
            list(RecordingBarLengthEnum), self.selected_recording_bar_length, go_next
        )
        StatusBar.show_message("SCENE RECORDING : %s" % self.selected_recording_bar_length)
        DomainEventBus.notify(SelectedRecordingBarLengthUpdatedEvent())

    def _get_track_recorder_factory(self, track):
        # type: (AbstractTrack) -> AbstractTrackRecorderFactory
        if isinstance(track, SimpleTrack):
            return TrackRecorderSimpleFactory(track, self._song, self.selected_recording_bar_length.bar_length_value)
        elif isinstance(track, ExternalSynthTrack):
            return TrackRecorderExternalSynthFactory(track, self._song, self.selected_recording_bar_length.bar_length_value)
        else:
            raise Protocol0Warning("This track is not recordable")

    def record_track(self, track, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        # assert there is a scene we can record on
        if self._recorder:
            self.cancel_record()
            raise Protocol0Warning("the track is recording")

        recorder_factory = self._get_track_recorder_factory(track)
        recording_scene_index = recorder_factory.get_recording_scene_index(record_type)

        seq = Sequence()
        if recording_scene_index is None:
            recording_scene_index = len(SongFacade.scenes())
            seq.add(self._song.create_scene)

        bar_length = recorder_factory.get_recording_bar_length(record_type)
        count_in = recorder_factory.create_count_in(record_type)
        recorder = recorder_factory.create_recorder(record_type, bar_length)
        recorder.set_recording_scene_index(recording_scene_index)

        seq.add(partial(self._start_recording, count_in, recorder, bar_length))
        return seq.done()

    def _start_recording(self, count_in, recorder, bar_length):
        # type: (CountInInterface, AbstractTrackRecorder, int) -> Optional[Sequence]
        bar_legend = bar_length if bar_length else "unlimited"
        StatusBar.show_message("Starting recording of %s bars on scene %s" % (bar_legend, recorder.recording_scene_index))

        seq = Sequence()
        seq.add(recorder.pre_record)
        seq.add(count_in.launch)
        seq.add(partial(recorder.record, bar_length=bar_length))
        seq.add(recorder.post_audio_record)
        seq.add(SongFacade.selected_scene().fire)
        seq.add(wait_for_event=BarEndingEvent)
        seq.add(partial(recorder.post_record, bar_length=bar_length))
        seq.add(partial(setattr, self, "_recorder", None))

        return seq.done()

    def cancel_record(self):
        # type: () -> None
        System.client().show_warning("Cancelling record")
        Scheduler.restart()
        self._recorder.cancel_record()
        self._recorder = None
