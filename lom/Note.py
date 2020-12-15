from a_protocol_0.lom.AbstractObject import AbstractObject


class Note(AbstractObject):
    MIN_DURATION = 1 / 128

    def __init__(self, pitch, start, duration, velocity, muted, *a, **k):
        super(Note, self).__init__(*a, **k)
        self._pitch = pitch
        self._start = start
        self._duration = duration
        self._velocity = velocity
        self._muted = muted

    def __repr__(self):
        return "{pitch:%s, start:%s, duration:%s, velocity:%s, muted:%s}" % (
            self.pitch, self.start, self.duration, self.velocity, self.muted)

    def to_data(self):
        return (self.pitch, self.start, self.duration, self.velocity, self.muted)

    @property
    def pitch(self):
        if self._pitch < 0:
            return 0
        if self._pitch > 127:
            return 127
        return int(self._pitch)

    @property
    def start(self):
        if self._start <= 0:
            return 0
        return float(self._start)

    @property
    def duration(self):
        if self._duration <= Note.MIN_DURATION:
            return Note.MIN_DURATION
        return float(self._duration)

    @property
    def velocity(self):
        if self._velocity < 0:
            return 0
        if self._velocity > 127:
            return 127
        return int(self._velocity)

    @property
    def muted(self):
        return bool(self._muted)
