from typing import Any, Iterable, Optional

from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.track_list.FoldActionEnum import FoldActionEnum
from protocol0.domain.lom.track.track_list.UserMutableSequence import UserMutableSequence
from protocol0.shared.SongFacade import SongFacade


class AbstractTrackList(UserMutableSequence):
    """ Manipulate a track list as an object """

    def __init__(self, abstract_tracks, default_abstract_tracks=None, *a, **k):
        # type: (Iterable[AbstractTrack], Optional[Iterable[AbstractTrack]], Any, Any) -> None
        tracks = list(dict.fromkeys(abstract_tracks))
        if not len(tracks) and default_abstract_tracks is not None:
            tracks = list(dict.fromkeys(default_abstract_tracks))
        super(AbstractTrackList, self).__init__(object_list=tracks, *a, **k)
        self._abstract_tracks = tracks

    @property
    def abstract_group_tracks(self):
        # type: () -> Iterable[AbstractGroupTrack]
        return (ab for ab in self._abstract_tracks if isinstance(ab, AbstractGroupTrack))

    @property
    def other_abstract_group_tracks(self):
        # type: () -> Iterable[AbstractGroupTrack]
        return (ab for ab in self.abstract_group_tracks if not ab.is_parent(SongFacade.current_track()))

    def toggle_fold(self, fold_action=None):
        # type: (Optional[FoldActionEnum]) -> None
        fold_action = fold_action or self._get_fold_action()
        if fold_action == FoldActionEnum.FOLD_ALL:
            for abg in self.abstract_group_tracks:
                abg.is_folded = True
        elif fold_action == FoldActionEnum.FOLD_ALL_EXCEPT_CURRENT:
            for abg in self.other_abstract_group_tracks:
                if not abg.is_armed:
                    abg.is_folded = True

            SongFacade.current_track().is_folded = False
            group_track = SongFacade.selected_track().group_track
            while group_track:
                group_track.is_folded = False
                group_track = group_track.group_track
        elif fold_action == FoldActionEnum.UNFOLD_ALL:
            for abg in self.abstract_group_tracks:
                abg.is_folded = False

    def _get_fold_action(self):
        # type: () -> FoldActionEnum
        """ Depending on the tracks fold state we change folding strategy """
        other_abstract_tracks_to_fold = [abg for abg in self.other_abstract_group_tracks if not abg.is_folded]

        if not SongFacade.current_track().is_folded:
            return FoldActionEnum.FOLD_ALL
        else:
            if len(other_abstract_tracks_to_fold):
                return FoldActionEnum.FOLD_ALL
            else:
                return FoldActionEnum.UNFOLD_ALL
