from functools import partial

from typing import Callable, Optional, Any, Dict

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.ActionEnum import ActionEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.lom.track.AbstractTrackList import AbstractTrackList


class KeywordActionManager(AbstractControlSurfaceComponent):
    MAPPING = {}  # type: Dict[ActionEnum, Callable]

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(KeywordActionManager, self).__init__(*a, **k)
        self.MAPPING = {
            ActionEnum.NEXT: lambda: self.parent.keywordSearchManager.search_track(
                self.parent.keywordSearchManager.LAST_SEARCH),
            ActionEnum.ARM: lambda: self.song.current_track.toggle_arm,
            ActionEnum.SOLO: lambda: self.song.current_track.toggle_solo,
            ActionEnum.REC: lambda: partial(self.song.current_track.record, RecordTypeEnum.NORMAL),
            ActionEnum.FOLD: lambda: AbstractTrackList(self.song.abstract_tracks).toggle_fold(),
            ActionEnum.UNDO: self.song.undo,
            ActionEnum.DUPLICATE: lambda: self.parent.trackManager.duplicate_current_track,
            ActionEnum.LOOP: lambda: self.song.selected_scene.toggle_solo,
            ActionEnum.SHOW: lambda: self.song.selected_scene.toggle_solo,
        }

    def execute_from_enum(self, command):
        # type: (ActionEnum) -> Optional[Callable]
        if command not in self.MAPPING:
            self.parent.log_error("Couldn't find %s in mapping" % command)
            return None

        self.parent.log_info("Executing %s" % command)
        func = self.MAPPING[command]()
        func()
