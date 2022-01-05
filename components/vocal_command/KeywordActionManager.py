from functools import partial

from typing import Any, Dict

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.enums.vocal_command.ActionEnum import ActionEnum
from protocol0.interface.EncoderAction import EncoderAction
from protocol0.interface.EncoderMoveEnum import EncoderMoveEnum
from protocol0.lom.track.AbstractTrackList import AbstractTrackList


class KeywordActionManager(AbstractControlSurfaceComponent):
    MAPPING = {}  # type: Dict[ActionEnum, EncoderAction]

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(KeywordActionManager, self).__init__(*a, **k)
        callable_dict = {
            ActionEnum.PLAY: self.song.play,
            ActionEnum.PAUSE: self.song.stop_playing,
            ActionEnum.STOP: lambda: self.song.reset(),
            ActionEnum.NEXT: lambda: self.parent.keywordSearchManager.search_track(
                self.parent.keywordSearchManager.LAST_SEARCH),
            ActionEnum.ARM: lambda: self.song.current_track.toggle_arm,
            ActionEnum.MONITOR: lambda: self.song.current_track.switch_monitoring,
            ActionEnum.SOLO: lambda: self.song.current_track.toggle_solo,
            ActionEnum.REC: lambda: partial(self.song.current_track.record, RecordTypeEnum.NORMAL),
            ActionEnum.FOLD: lambda: AbstractTrackList(self.song.abstract_tracks).toggle_fold(),
            ActionEnum.CLEAR: self.parent.logManager.clear,
            ActionEnum.DUPLICATE: lambda: self.song.current_track.duplicate,
            ActionEnum.LOOP: lambda: self.song.selected_scene.toggle_loop,
            ActionEnum.SHOW: lambda: self.song.current_track.show_hide_instrument,
            # ActionEnum.PUSH: self.parent.push2Manager.connect_push2,
            ActionEnum.SPLIT: lambda: self.song.selected_scene.split,
        }
        for enum, func in callable_dict.items():
            self.MAPPING[enum] = EncoderAction(func, move_type=EncoderMoveEnum.API, name=None)

    def execute_from_enum(self, action_enum):
        # type: (ActionEnum) -> None
        if action_enum not in self.MAPPING:
            self.parent.log_error("Couldn't find %s in mapping" % action_enum)
            return None

        encoder_action = self.MAPPING[action_enum]
        encoder_action.execute(encoder_name="speech")
