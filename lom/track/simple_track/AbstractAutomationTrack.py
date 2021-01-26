from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractAutomationTrack(SimpleTrack):
    def __init__(self, *a, **k):
        super(AbstractAutomationTrack, self).__init__(*a, **k)
        self._is_hearable = False
