from typing import Callable

from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.shared.sequence.Sequence import Sequence


class TrackCrudComponent(object):
    def __init__(self, create_midi_track, create_audio_track, duplicate_track, delete_track):
        # type: (Callable, Callable, Callable, Callable) -> None
        self._create_midi_track = create_midi_track
        self._create_audio_track = create_audio_track
        self._duplicate_track = duplicate_track
        self._delete_track = delete_track

    def create_midi_track(self, index):
        # type: (int) -> Sequence
        seq = Sequence()
        self._create_midi_track(Index=index)
        seq.wait_for_event(TracksMappedEvent)
        return seq.done()

    def create_audio_track(self, index):
        # type: (int) -> Sequence
        seq = Sequence()
        self._create_audio_track(Index=index)
        seq.wait_for_event(TracksMappedEvent)
        return seq.done()

    def duplicate_track(self, index):
        # type: (int) -> Sequence
        seq = Sequence()
        self._duplicate_track(index)
        seq.wait_for_event(TracksMappedEvent)
        return seq.done()

    def delete_track(self, index):
        # type: (int) -> Sequence
        seq = Sequence()
        self._delete_track(index)
        seq.wait_for_event(TracksMappedEvent)
        return seq.done()
