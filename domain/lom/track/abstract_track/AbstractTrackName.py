import re

from typing import TYPE_CHECKING, Optional

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack


class AbstractTrackName(UseFrameworkEvents):
    DEBUG = True

    def __init__(self, track):
        # type: (AbstractTrack) -> None
        super(AbstractTrackName, self).__init__()
        self._track = track
        self._name_listener.subject = self._track._track

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        Scheduler.defer(self.update)

    def get_base_name(self):
        # type: () -> str
        match = re.match(
            "^(?P<base_name>[^()]*).*$", self._track.name
        )
        base_name = match.group("base_name").strip() if match else ""

        if self.DEBUG:
            Logger.info("%s <-> %s <-> %s" % (base_name, self._should_recompute_base_name(base_name=base_name), self._track.computed_base_name))
        # allows manual modification
        if self._should_recompute_base_name(base_name=base_name):
            return self._track.computed_base_name
        else:
            return base_name

    def _should_recompute_base_name(self, base_name):
        # type: (unicode) -> bool
        from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack

        return (
                not base_name
                or base_name.lower() == self._track.DEFAULT_NAME.lower()
                or self._track.instrument is not None
                or isinstance(self._track, SimpleDummyTrack)
        )

    def update(self, name=None):
        # type: (Optional[str]) -> None
        name = name or self.get_base_name()

        if name[0:1].islower():
            name = name.title()

        from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack

        if isinstance(self._track, NormalGroupTrack):
            name += " (%d)" % len(self._track.sub_tracks)

        self._track.name = name
