import re

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Optional, Callable

from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger


class AbstractTrackName(SlotManager):
    _DEBUG = False

    def __init__(self, live_track, default_name, computed_base_name):
        # type: (Live.Track.Track, str, Callable) -> None
        super(AbstractTrackName, self).__init__()
        self._live_track = live_track
        self._default_name = default_name
        self._computed_base_name = computed_base_name
        self._name_listener.subject = live_track

    @subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        Scheduler.defer(self.update)

    def get_base_name(self):
        # type: () -> str
        match = re.match(
            "^(?P<base_name>[^()]*).*$", self._live_track.name
        )
        base_name = match.group("base_name").strip() if match else ""

        if self._DEBUG:
            Logger.info("%s <-> %s <-> %s" % (
                base_name,
                self._should_recompute_base_name(base_name=base_name),
                self._computed_base_name()
            ))
        # allows manual modification
        if self._should_recompute_base_name(base_name=base_name):
            return self._computed_base_name()
        else:
            return base_name

    def _should_recompute_base_name(self, base_name):
        # type: (unicode) -> bool
        from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack

        return (
                not base_name
                or base_name.lower() == self._default_name.lower()
                # or self._track.instrument is not None # nb activating this blocks manual changes
                or isinstance(self._live_track, SimpleDummyTrack)
        )

    def update(self, name=None):
        # type: (Optional[str]) -> None
        name = name or self.get_base_name()

        if name[0:1].islower():
            name = name.title()

        from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack

        if isinstance(self._live_track, NormalGroupTrack):
            name += " (%d)" % len(self._live_track.sub_tracks)

        self._live_track.name = name
