from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.count_in.count_in_interface import CountInInterface
from protocol0.domain.track_recorder.count_in.count_in_one_bar import CountInOneBar
from protocol0.domain.track_recorder.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.domain.track_recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.domain.track_recorder.simple.track_recorder_simple import TrackRecorderSimple
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class TrackRecorderSimpleFactory(AbstractTrackRecorderFactory):
    def __init__(self, track, song, recording_bar_length):
        # type: (SimpleTrack, Song, int) -> None
        super(TrackRecorderSimpleFactory, self).__init__()
        self.track = track
        self._song = song
        self._recording_bar_length = recording_bar_length

    def create_count_in(self, _):
        # type: (RecordTypeEnum) -> CountInInterface
        return CountInOneBar(self.track, self._song)

    def _create_recorder(self, _):
        # type: (RecordTypeEnum) -> AbstractTrackRecorder
        return TrackRecorderSimple(self.track, self._song)

    def _get_recording_scene_index(self, _):
        # type: (RecordTypeEnum) -> Optional[int]
        for i in range(SongFacade.selected_scene().index, len(SongFacade.scenes())):
            if not self.track.clip_slots[i].clip:
                return i

        return None

    def get_recording_bar_length(self, _):
        # type: (RecordTypeEnum) -> int
        return self._recording_bar_length