from typing import Dict, Type, Optional

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.enums.ColorEnum import ColorEnum
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.Song import Song
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.validation.AbstractObjectValidator import AbstractObjectValidator
from protocol0.validation.object_validators.ExternalSynthTrackValidator import ExternalSynthTrackValidator
from protocol0.validation.object_validators.SimpleAudioTailTrackValidator import SimpleAudioTailTrackValidator
from protocol0.validation.object_validators.SimpleAudioTrackValidator import SimpleAudioTrackValidator
from protocol0.validation.object_validators.SimpleInstrumentBusTrackValidator import SimpleInstrumentBusTrackValidator
from protocol0.validation.object_validators.SongValidator import SongValidator


class ValidatorManager(AbstractControlSurfaceComponent):
    VALIDATOR_MAPPING = {
        ExternalSynthTrack: ExternalSynthTrackValidator,
        SimpleAudioTrack: SimpleAudioTrackValidator,
        SimpleInstrumentBusTrack: SimpleInstrumentBusTrackValidator,
        SimpleAudioTailTrack: SimpleAudioTailTrackValidator,
        Song: SongValidator
    }  # type: Dict[Type[AbstractObject], Type[AbstractObjectValidator]]

    def _get_object_validator(self, obj, log=True):
        # type: (AbstractObject, Optional[bool]) -> Optional[AbstractObjectValidator]
        cls = obj.__class__
        if cls not in self.VALIDATOR_MAPPING:
            return None

        return self.VALIDATOR_MAPPING[cls](obj, log=log)

    def validate_object(self, obj, log=False):
        # type: (AbstractObject, bool) -> bool
        validator = self._get_object_validator(obj, log=log)
        if not validator or validator.is_valid():
            if log:
                self.parent.show_message("%s is valid" % obj)
            obj.refresh_appearance()
            return True

        self.parent.log_warning(validator.get_error_message())
        if hasattr(obj, "color"):
            obj.color = ColorEnum.ERROR.index
        return False

    def fix_object(self, obj):
        # type: (AbstractObject) -> None
        if self.validate_object(obj, log=True):
            return None

        validator = self._get_object_validator(obj)
        validator.fix()
        obj.refresh_appearance()
