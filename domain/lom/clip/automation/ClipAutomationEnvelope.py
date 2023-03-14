import Live

from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.utils.utils import float_seq


class ClipAutomationEnvelope(object):
    _FOOTPRINT_MEASURES = 100

    def __init__(self, envelope, length):
        # type: (Live.Clip.AutomationEnvelope, float) -> None
        self._envelope = envelope
        self._length = length

    @property
    def hash(self):
        # type: () -> float
        """pick up to 10 values to generate a footprint of the automation"""
        values = [
            self.value_at_time(i)
            for i in float_seq(0, int(self._length), self._length / self._FOOTPRINT_MEASURES)
        ]
        values.append(self.value_at_time(self._length))

        return hash(tuple(values))

    def value_at_time(self, beat_length):
        # type: (float) -> float
        return self._envelope.value_at_time(beat_length)

    def insert_step(self, start_beat, beat_length, value):
        # type: (float, float, float) -> None
        self._envelope.insert_step(start_beat, beat_length, value)

    def create_start_and_end_points(self):
        # type: () -> None
        """we need to emulate an automation value at the beginning and the end of the clip
        so that doing ctrl-a will select the automation on the whole clip duration
        """
        self.insert_step(0, 0, self.value_at_time(0))
        self.insert_step(self._length, 0, self.value_at_time(self._length))

    def copy(self):
        # type: () -> None
        self.create_start_and_end_points()
        Backend.client().select_and_copy()

    def paste(self):
        # type: () -> None
        self.create_start_and_end_points()
        Backend.client().select_and_paste()

    @classmethod
    def focus(cls):
        # type: () -> None
        Backend.client().move_to(1225, 1013)
