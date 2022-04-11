import os

from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.shared.Config import Config


class DrumsTrack(NormalGroupTrack):
    DEFAULT_NAME = "Drums"

    def __init__(self, base_group_track):
        # type: (SimpleTrack) -> None
        super(DrumsTrack, self).__init__(base_group_track)
        self.categories = [d.lower() for d in os.listdir(Config.SAMPLE_PATH) if not d.startswith("_")]

    @property
    def computed_base_name(self):
        # type: () -> str
        return self.DEFAULT_NAME
