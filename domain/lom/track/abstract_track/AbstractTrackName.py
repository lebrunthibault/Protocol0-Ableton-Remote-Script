import re

from typing import TYPE_CHECKING, Any, Optional

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.shared.decorators import p0_subject_slot
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack


class AbstractTrackName(UseFrameworkEvents):
    DEBUG = False

    def __init__(self, track, *a, **k):
        # type: (AbstractTrack, Any, Any) -> None
        super(AbstractTrackName, self).__init__(*a, **k)
        self.track = track
        self._name_listener.subject = self.track._track
        self._disconnected = False

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        Scheduler.defer(self.update)

    def _get_base_name(self):
        # type: () -> str
        match = re.match(
            "^(?P<base_name>[^()]*).*$", self.track.name
        )
        base_name = match.group("base_name").strip() if match else ""

        if self.DEBUG:
            Logger.log_info("%s <-> %s <-> %s" % (base_name, self._should_recompute_base_name(base_name=base_name), self.track.computed_base_name))
        # allows manual modification
        if self._should_recompute_base_name(base_name=base_name):
            return self.track.computed_base_name
        else:
            return base_name

    def _should_recompute_base_name(self, base_name):
        # type: (unicode) -> bool
        from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack

        return (
                not base_name
                or base_name.lower() == self.track.DEFAULT_NAME.lower()
                or isinstance(self.track, SimpleDummyTrack)
        )

    def update(self, name=None):
        # type: (Optional[str]) -> None
        if self._disconnected:
            return
        name = name or self._get_base_name()

        if name[0:1].islower():
            name = name.title()

        from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack

        if isinstance(self.track, NormalGroupTrack):
            name += " (%d)" % len(self.track.sub_tracks)

        self.track.name = name

    def disconnect(self):
        # type: () -> None
        super(AbstractTrackName, self).disconnect()
        self._disconnected = True
