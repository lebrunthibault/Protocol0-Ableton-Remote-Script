import Live

from protocol0.domain.lom.clip.ClipEnvelopeShowedEvent import ClipEnvelopeShowedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class RecordingComponent(object):
    def __init__(self, song):
        # type: (Live.Song.Song) -> None
        self._song = song
        DomainEventBus.subscribe(ClipEnvelopeShowedEvent, lambda _: self.re_enable_automation())

    @property
    def back_to_arranger(self):
        # type: () -> bool
        return self._song.back_to_arranger

    @back_to_arranger.setter
    def back_to_arranger(self, back_to_arranger):
        # type: (bool) -> None
        self._song.back_to_arranger = back_to_arranger

    @property
    def session_record(self):
        # type: () -> bool
        return self._song.session_record

    @session_record.setter
    def session_record(self, session_record):
        # type: (bool) -> None
        self._song.session_record = session_record

    @property
    def record_mode(self):
        # type: () -> bool
        return self._song.record_mode

    @record_mode.setter
    def record_mode(self, record_mode):
        # type: (bool) -> None
        self._song.record_mode = record_mode

    @property
    def session_automation_record(self):
        # type: () -> bool
        return self._song.session_automation_record

    @session_automation_record.setter
    def session_automation_record(self, session_automation_record):
        # type: (bool) -> None
        self._song.session_automation_record = session_automation_record

    def re_enable_automation(self):
        # type: () -> None
        self._song.re_enable_automation()
