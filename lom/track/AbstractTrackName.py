import re

from typing import TYPE_CHECKING, Any

from protocol0.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.lom.AbstractObjectName import AbstractObjectName

if TYPE_CHECKING:
    from protocol0.lom.track.AbstractTrack import AbstractTrack


class AbstractTrackName(AbstractObjectName):
    DEBUG = False

    def __init__(self, track, *a, **k):
        # type: (AbstractTrack, Any, Any) -> None
        super(AbstractTrackName, self).__init__(*a, **k)
        self.track = track
        self._name_listener.subject = self.track._track
        self._disconnected = False

    def _get_base_name(self):
        # type: () -> str
        match = re.match(
            "^(?P<base_name>[^()]*).*$", self.track.name
        )
        base_name = match.group("base_name").strip() if match else ""

        if self.DEBUG:
            self.parent.log_info("%s <-> %s <-> %s" % (base_name, self._should_recompute_base_name(base_name=base_name), self.track.computed_base_name))
        # allows manual modification
        if self._should_recompute_base_name(base_name=base_name):
            return self.track.computed_base_name
        else:
            return base_name

    def _should_recompute_base_name(self, base_name):
        # type: () -> bool
        from protocol0.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack

        return (
                not base_name
                or base_name.lower() == self.track.DEFAULT_NAME.lower()
                or base_name.split("-")[0].isnumeric()
                or (
                        self.track.instrument
                        and self.track.instrument.PRESET_DISPLAY_OPTION != PresetDisplayOptionEnum.NONE
                )
                or isinstance(self.track, SimpleDummyTrack)
        )

    def update(self):
        # type: () -> None
        if self._disconnected:
            return
        name = self._get_base_name()

        if name[0:1].islower():
            name = name.title()

        from protocol0.lom.track.group_track.NormalGroupTrack import NormalGroupTrack

        if isinstance(self.track, NormalGroupTrack):
            name += " (%d)" % len(self.track.sub_tracks)

        self.track.name = name

    def disconnect(self):
        # type: () -> None
        super(AbstractTrackName, self).disconnect()
        self._disconnected = True
