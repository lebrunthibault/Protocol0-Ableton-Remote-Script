from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.EmptyValidator import EmptyValidator
from protocol0.domain.lom.validation.object_validators.ExternalSynthTrackValidator import ExternalSynthTrackValidator
from protocol0.domain.lom.validation.object_validators.SceneValidator import SceneValidator
from protocol0.domain.lom.validation.object_validators.SimpleAudioTailTrackValidator import \
    SimpleAudioTailTrackValidator
from protocol0.domain.lom.validation.object_validators.SimpleAudioTrackValidator import SimpleAudioTrackValidator
from protocol0.domain.lom.validation.object_validators.SimpleInstrumentBusTrackValidator import \
    SimpleInstrumentBusTrackValidator
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning


class ValidatorFactory(object):
    def __init__(self, browser_service):
        # type: (BrowserServiceInterface) -> None
        self._browser_service = browser_service

    def create_from_object(self, obj):
        # type: (object) -> ValidatorInterface
        if isinstance(obj, Scene):
            return SceneValidator(obj)
        elif isinstance(obj, ExternalSynthTrack):
            return ExternalSynthTrackValidator(obj, self._browser_service)
        elif isinstance(obj, SimpleAudioTrack):
            return SimpleAudioTrackValidator(obj)
        elif isinstance(obj, SimpleInstrumentBusTrack):
            return SimpleInstrumentBusTrackValidator(obj)
        elif isinstance(obj, SimpleAudioTailTrack):
            return SimpleAudioTailTrackValidator(obj)
        elif isinstance(obj, AbstractTrack):
            # no validation
            return EmptyValidator()
        else:
            raise Protocol0Warning("%s is not handled by the object validator" % obj)
