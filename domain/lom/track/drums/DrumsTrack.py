from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack


class DrumsTrack(NormalGroupTrack):
    DEFAULT_NAME = "Drums"

    @property
    def computed_base_name(self):
        # type: () -> str
        return self.DEFAULT_NAME
