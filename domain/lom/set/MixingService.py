from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.shared.SongFacade import SongFacade


class MixingService(UseFrameworkEvents):
    def scroll_all_tracks_volume(self, go_next):
        # type: (bool) -> None
        for track in SongFacade.abstract_tracks():
            if isinstance(track, NormalGroupTrack):
                continue
            if "kick" in track.name.lower():
                continue
            track.scroll_volume(go_next=go_next)
