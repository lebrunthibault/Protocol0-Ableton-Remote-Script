from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.recorder.track_recorder_decorator.track_recorder_count_in_one_bar_decorator import TrackRecorderCountInOneBarDecorator
from protocol0.recorder.track_recorder_decorator.track_recorder_count_in_short_decorator import TrackRecorderCountInShortDecorator
from protocol0.recorder.track_recorder_decorator.track_recorder_focus_empty_clip_slot_decorator import \
    TrackRecorderFocusEmptyClipSlotDecorator
from protocol0.recorder.track_recorder_interface import TrackRecorderInterface


class AbstractTrackRecorderFactory(AbstractObject):
    @classmethod
    def create_track_recorder(cls, track, record_type, bar_length):
        # type: (AbstractTrack, RecordTypeEnum, BarLengthEnum) -> TrackRecorderInterface
        recorder = cls.create_recorder(track, record_type, bar_length)

        if recorder is None:
            raise Protocol0Error("Couldn't generate recorder")

        # apply common decorators
        if record_type == RecordTypeEnum.NORMAL:
            recorder = TrackRecorderFocusEmptyClipSlotDecorator(recorder)
            recorder = TrackRecorderCountInOneBarDecorator(recorder)
        else:
            recorder = TrackRecorderCountInShortDecorator(recorder)

        return recorder

    @classmethod
    def create_recorder(cls, track, record_type, bar_length):
        # type: (AbstractTrack, RecordTypeEnum, BarLengthEnum) -> TrackRecorderInterface
        raise NotImplementedError
