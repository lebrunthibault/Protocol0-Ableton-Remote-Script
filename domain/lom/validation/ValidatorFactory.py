from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface
from protocol0.domain.lom.validation.object_validators.ExternalSynthTrackValidator import ExternalSynthTrackValidator
from protocol0.domain.lom.validation.object_validators.SimpleAudioTailTrackValidator import SimpleAudioTailTrackValidator
from protocol0.domain.lom.validation.object_validators.SimpleAudioTrackValidator import SimpleAudioTrackValidator
from protocol0.domain.lom.validation.object_validators.SimpleInstrumentBusTrackValidator import SimpleInstrumentBusTrackValidator
from protocol0.domain.lom.validation.object_validators.SongValidator import SongValidator


class ValidatorFactory(object):
    @classmethod
    def create_from_object(cls, obj):
        # type: (AbstractObject) -> ValidatorInterface
        from protocol0.domain.lom.song.Song import Song

        if isinstance(obj, ExternalSynthTrack):
            return ExternalSynthTrackValidator(obj)
        elif isinstance(obj, SimpleAudioTrack):
            return SimpleAudioTrackValidator(obj)
        elif isinstance(obj, SimpleInstrumentBusTrack):
            return SimpleInstrumentBusTrackValidator(obj)
        elif isinstance(obj, SimpleAudioTailTrack):
            return SimpleAudioTailTrackValidator(obj)
        elif isinstance(obj, Song):
            return SongValidator(obj)
        else:
            raise Protocol0Error("object of class %s has not validator" % obj.__class__.__name__)
