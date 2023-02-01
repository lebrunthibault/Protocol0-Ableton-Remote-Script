from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.shared.Song import Song


class MixingService(object):
    def scroll_all_tracks_volume(self, go_next):
        # type: (bool) -> None
        for track in Song.abstract_tracks():
            if isinstance(track, NormalGroupTrack):
                continue
            track.base_track.scroll_volume(go_next)
