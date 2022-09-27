from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class ReferenceTrack(SimpleTrack):
    TRACK_NAME = "Reference"

    def toggle(self):
        # type: () -> None
        if self.muted:
            self.muted = False
            self.solo = True
        else:
            self.muted = True
            self.solo = False
