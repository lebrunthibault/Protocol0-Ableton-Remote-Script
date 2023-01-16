from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.shared.AbstractEnum import AbstractEnum


class RecordTypeEnum(AbstractEnum):
    MIDI = "Midi"
    MIDI_UNLIMITED = "Midi unlimited"
    AUDIO = "Audio"
    AUDIO_FULL = "Audio full"
    AUDIO_MULTI_SCENE = "Audio multi scene"

    @property
    def records_midi(self):
        # type: () -> bool
        return self in (
            RecordTypeEnum.MIDI,
            RecordTypeEnum.MIDI_UNLIMITED,
        )

    def get_count_in(self):
        # type: () -> CountInInterface
        from protocol0.domain.track_recorder.count_in.CountInOneBar import CountInOneBar
        from protocol0.domain.track_recorder.count_in.CountInShort import CountInShort

        if self.records_midi:
            return CountInOneBar()
        else:
            return CountInShort()

