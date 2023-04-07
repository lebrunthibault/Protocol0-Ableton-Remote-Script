from protocol0.domain.lom.device.DrumRackService import DrumRackService
from protocol0.domain.lom.instrument.instrument.InstrumentDrumRack import InstrumentDrumRack
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.validation.ValidatorFactory import ValidatorFactory
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.logging.Logger import Logger


class ValidatorService(object):
    def __init__(self, validator_factory, drum_rack_service):
        # type: (ValidatorFactory, DrumRackService) -> None
        self._validator_factory = validator_factory
        self._drum_rack_service = drum_rack_service

    def validate_object(self, obj):
        # type: (object) -> bool
        validator = self._validator_factory.create_from_object(obj)
        if validator.is_valid():
            return True
        else:
            Logger.warning(validator.get_error_message())
            return False

    def fix_object(self, obj, log=True):
        # type: (object, bool) -> None
        validator = self._validator_factory.create_from_object(obj)
        if validator.is_valid():
            message = "%s is valid" % obj
        else:
            if log:
                Logger.warning(validator.get_error_message())
            validator.fix()
            message = "Fixed %s" % obj

        Logger.info(message)
        if log:
            Backend.client().show_success(message)

        if hasattr(obj, "appearance") and hasattr(obj.appearance, "refresh"):  # type: ignore
            obj.appearance.refresh()  # type: ignore

        if isinstance(obj, SimpleTrack) and isinstance(obj.instrument, InstrumentDrumRack):
            self._drum_rack_service.clean_racks(obj.instrument)
