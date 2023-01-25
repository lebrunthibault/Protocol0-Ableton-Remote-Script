from functools import partial

import Live

from protocol0.domain.lom.clip.ClipEnvelopeShowedEvent import ClipEnvelopeShowedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.timing import defer
from protocol0.domain.track_recorder.event.RecordEndedEvent import RecordEndedEvent
from protocol0.domain.track_recorder.event.RecordStartedEvent import RecordStartedEvent
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class RecordingComponent(object):
    def __init__(self, song):
        # type: (Live.Song.Song) -> None
        self._live_song = song
        DomainEventBus.subscribe(ClipEnvelopeShowedEvent, lambda _: song.re_enable_automation())
        DomainEventBus.subscribe(RecordStartedEvent, self._on_record_started_event)
        DomainEventBus.subscribe(RecordEndedEvent, self._on_record_ended_event)

    @defer
    def _on_record_started_event(self, event):
        # type: (RecordStartedEvent) -> None
        recording_scene = Song.scenes()[event.scene_index]
        recording_scene.fire()
        seq = Sequence()
        if event.has_count_in:
            seq.defer()
        seq.add(partial(self._start_session_record, event))
        seq.done()

    def _start_session_record(self, event):
        # type: (RecordStartedEvent) -> None
        self.session_automation_record = True
        self.session_record = True
        if event.full_record:
            self.record_mode = True

    def _on_record_ended_event(self, _):
        # type: (RecordEndedEvent) -> None
        self.session_automation_record = False
        self.session_record = False

    @property
    def back_to_arranger(self):
        # type: () -> bool
        return self._live_song.back_to_arranger

    @back_to_arranger.setter
    def back_to_arranger(self, back_to_arranger):
        # type: (bool) -> None
        self._live_song.back_to_arranger = back_to_arranger

    @property
    def session_record(self):
        # type: () -> bool
        return self._live_song.session_record

    @session_record.setter
    def session_record(self, session_record):
        # type: (bool) -> None
        self._live_song.session_record = session_record

    @property
    def record_mode(self):
        # type: () -> bool
        return self._live_song.record_mode

    @record_mode.setter
    def record_mode(self, record_mode):
        # type: (bool) -> None
        self._live_song.record_mode = record_mode

    @property
    def session_automation_record(self):
        # type: () -> bool
        return self._live_song.session_automation_record

    @session_automation_record.setter
    def session_automation_record(self, session_automation_record):
        # type: (bool) -> None
        self._live_song.session_automation_record = session_automation_record
