from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.track.AbstractTrack import AbstractTrack


class ValidatorManager(AbstractControlSurfaceComponent):
    def validate_track(self, abstract_track):
        # type: (AbstractTrack) -> None
        abstract_track.is_configuration_valid = abstract_track.validate_configuration()
        if not abstract_track.is_configuration_valid:
            abstract_track.refresh_appearance()
