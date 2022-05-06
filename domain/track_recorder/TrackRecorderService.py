from functools import partial

from typing import Optional

from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.AbstractTrackRecorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.AbstractTrackRecorderFactory import AbstractTrackRecorderFactory
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.TrackRecordingCancelledEvent import TrackRecordingCancelledEvent
from protocol0.domain.track_recorder.TrackRecordingStartedEvent import TrackRecordingStartedEvent
from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthFactory import \
    TrackRecorderExternalSynthFactory
from protocol0.domain.track_recorder.recording_bar_length.RecordingBarLengthEnum import RecordingBarLengthEnum
from protocol0.domain.track_recorder.recording_bar_length.RecordingBarLengthScroller import RecordingBarLengthScroller
from protocol0.domain.track_recorder.simple.TrackRecoderSimpleFactory import TrackRecorderSimpleFactory
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderService(object):
    def __init__(self, playback_component, recording_component, scene_crud_component):
        # type: (PlaybackComponent, RecordingComponent, SceneCrudComponent) -> None
        self._playback_component = playback_component
        self._recording_component = recording_component
        self._scene_crud_component = scene_crud_component

        self.recording_bar_length_scroller = RecordingBarLengthScroller(RecordingBarLengthEnum.ONE)
        self._recorder = None  # type: Optional[AbstractTrackRecorder]

    @property
    def is_recording(self):
        # type: () -> bool
        return self._recorder is not None

    def _get_track_recorder_factory(self, track):
        # type: (AbstractTrack) -> AbstractTrackRecorderFactory
        if isinstance(track, SimpleTrack):
            factory_class = TrackRecorderSimpleFactory
        elif isinstance(track, ExternalSynthTrack):
            factory_class = TrackRecorderExternalSynthFactory  # type: ignore[assignment]
        else:
            raise Protocol0Warning("This track is not recordable")

        return factory_class(
            track,
            self._playback_component,
            self._recording_component,
            self.recording_bar_length_scroller.current_value.bar_length_value
        )

    def record_track(self, track, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        # we'll subscribe back later
        DomainEventBus.un_subscribe(SongStoppedEvent, self._on_song_stopped_event)
        if self._recorder is not None:
            self.cancel_record()
            DomainEventBus.emit(TrackRecordingCancelledEvent())
            return None

        recorder_factory = self._get_track_recorder_factory(track)
        recording_scene_index = recorder_factory.get_recording_scene_index(record_type)

        seq = Sequence()
        # assert there is a scene we can record on
        if recording_scene_index is None:
            recording_scene_index = len(SongFacade.scenes())
            seq.add(self._scene_crud_component.create_scene)

        bar_length = recorder_factory.get_recording_bar_length(record_type)

        count_in = recorder_factory.create_count_in(record_type)
        self._recorder = recorder_factory.create_recorder(record_type)
        self._recorder.set_recording_scene_index(recording_scene_index)

        Backend.client().show_info("Rec: %s" % self._recorder.legend(bar_length))

        seq.add(partial(self._start_recording, count_in, self._recorder, bar_length))
        return seq.done()

    def _start_recording(self, count_in, recorder, bar_length):
        # type: (CountInInterface, AbstractTrackRecorder, int) -> Optional[Sequence]
        DomainEventBus.emit(TrackRecordingStartedEvent(recorder.recording_scene_index))
        seq = Sequence()
        seq.add(recorder.pre_record)
        seq.add(count_in.launch)
        seq.add(partial(DomainEventBus.subscribe, SongStoppedEvent, self._on_song_stopped_event))
        seq.add(partial(recorder.record, bar_length))
        seq.add(recorder.post_audio_record)
        seq.add(partial(recorder.post_record, bar_length))
        seq.add(recorder.recording_scene.fire)
        seq.add(partial(setattr, self, "_recorder", None))

        return seq.done()

    def cancel_record(self):
        # type: () -> None
        Scheduler.restart()
        self._recorder.cancel_record()
        self._recorder = None
        Backend.client().show_warning("Recording cancelled")

    def _on_song_stopped_event(self, _):
        # type: (SongStoppedEvent) -> None
        """ happens when manually stopping song while recording."""
        if self._recorder is None:
            return
        else:
            # we could cancel the record here also
            Backend.client().show_info("Recording stopped")
            # deferring this to allow components to react to the song stopped event
            Scheduler.defer(Scheduler.restart)
            self._recorder = None
