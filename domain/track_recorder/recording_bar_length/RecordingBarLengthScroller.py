from typing import List

from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.recording_bar_length.RecordingBarLengthEnum import (
    RecordingBarLengthEnum,
)
from protocol0.domain.track_recorder.recording_bar_length.SelectedRecordingBarLengthUpdatedEvent import (
    SelectedRecordingBarLengthUpdatedEvent,
)
from protocol0.shared.logging.StatusBar import StatusBar


class RecordingBarLengthScroller(ValueScroller):
    def _get_values(self):
        # type: () -> List[RecordingBarLengthEnum]
        return list(RecordingBarLengthEnum)

    def _value_scrolled(self):
        # type: () -> None
        StatusBar.show_message("Fixed Recording : %s" % self.current_value)
        DomainEventBus.emit(SelectedRecordingBarLengthUpdatedEvent())
