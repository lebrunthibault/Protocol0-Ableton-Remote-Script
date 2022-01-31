from functools import partial

from typing import Any, Dict

from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.application.vocal_command.VocalActionEnum import VocalActionEnum
from protocol0.domain.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.application.faderfox.EncoderAction import EncoderAction
from protocol0.application.faderfox.EncoderMoveEnum import EncoderMoveEnum
from protocol0.domain.lom.track.AbstractTrackList import AbstractTrackList
from protocol0.application.decorators import handle_error


class KeywordActionManager(AbstractControlSurfaceComponent):
    MAPPING = {}  # type: Dict[VocalActionEnum, EncoderAction]

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(KeywordActionManager, self).__init__(*a, **k)
        callable_dict = {
            VocalActionEnum.PLAY: self.song.play,
            VocalActionEnum.PAUSE: self.song.stop_playing,
            VocalActionEnum.STOP: lambda: self.song.reset(),
            VocalActionEnum.NEXT: lambda: self.parent.keywordSearchManager.search_track(
                self.parent.keywordSearchManager.LAST_SEARCH),
            VocalActionEnum.ARM: lambda: self.song.current_track.toggle_arm,
            VocalActionEnum.MONITOR: lambda: self.song.current_external_synth_track.monitoring_state.switch,
            VocalActionEnum.SOLO: lambda: self.song.current_track.toggle_solo,
            VocalActionEnum.REC: lambda: partial(self.parent.trackRecorderManager.record_track, self.song.current_track,
                                                 RecordTypeEnum.NORMAL),
            VocalActionEnum.FOLD: lambda: AbstractTrackList(self.song.abstract_tracks).toggle_fold(),
            VocalActionEnum.CLEAR: self.parent.logManager.clear,
            VocalActionEnum.DUPLICATE: lambda: self.song.current_track.duplicate,
            VocalActionEnum.LOOP: lambda: self.song.selected_scene.toggle_loop,
            VocalActionEnum.SHOW: lambda: self.song.current_track.show_hide_instrument,
            VocalActionEnum.SPLIT: lambda: self.song.selected_scene.split,
        }
        for enum, func in callable_dict.items():
            self.MAPPING[enum] = EncoderAction(func, move_type=EncoderMoveEnum.API, name=None)

    @handle_error
    def execute_from_enum(self, action_enum):
        # type: (VocalActionEnum) -> None
        if action_enum not in self.MAPPING:
            self.parent.log_error("Couldn't find %s in mapping" % action_enum)
            return None

        encoder_action = self.MAPPING[action_enum]
        encoder_action.execute(encoder_name="speech")
