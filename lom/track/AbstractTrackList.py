from typing import Any, Iterable

from a_protocol_0.enums.FoldActionEnum import FoldActionEnum
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.utils.UserMutableSequence import UserMutableSequence


class AbstractTrackList(UserMutableSequence):
    """ Manipulate a track list as an object """

    def __init__(self, abstract_tracks, *a, **k):
        # type: (Iterable[AbstractTrack], Any, Any) -> None
        tracks = list(dict.fromkeys(abstract_tracks))
        super(AbstractTrackList, self).__init__(list=tracks, *a, **k)
        self._abstract_tracks = tracks

    @property
    def abstract_group_tracks(self):
        # type: () -> Iterable[AbstractGroupTrack]
        return (ab for ab in self._abstract_tracks if isinstance(ab, AbstractGroupTrack))

    @property
    def other_abstract_group_tracks(self):
        # type: () -> Iterable[AbstractGroupTrack]
        return (ab for ab in self.abstract_group_tracks if not ab.is_parent(self.song.current_track))

    def play_stop(self):
        # type: () -> None
        if any(abstract_track.is_playing for abstract_track in self._abstract_tracks):
            for t in self._abstract_tracks:
                t.stop()
        else:
            for t in self._abstract_tracks:
                t.play()

    def toggle_solo(self):
        # type: () -> None
        for t in self._abstract_tracks:
            t.solo = not t.solo

    def toggle_fold(self):
        # type: () -> None
        fold_action = self._get_fold_action()
        if fold_action == FoldActionEnum.FOLD_ALL:
            for abg in self.abstract_group_tracks:
                abg.is_folded = True
        elif fold_action == FoldActionEnum.FOLD_ALL_EXCEPT_CURRENT:
            for abg in self.other_abstract_group_tracks:
                abg.is_folded = True
        elif fold_action == FoldActionEnum.UNFOLD_ALL:
            for abg in self.abstract_group_tracks:
                abg.is_folded = False

    def _get_fold_action(self):
        # type: () -> FoldActionEnum
        """ Depending on the tracks fold state we change folding strategy """
        other_abstract_tracks_to_fold = [abg for abg in self.other_abstract_group_tracks if not abg.is_folded]

        if not self.song.current_track.is_folded:
            if len(other_abstract_tracks_to_fold):
                return FoldActionEnum.FOLD_ALL_EXCEPT_CURRENT
            else:
                return FoldActionEnum.FOLD_ALL
        else:
            if len(other_abstract_tracks_to_fold):
                return FoldActionEnum.FOLD_ALL
            else:
                return FoldActionEnum.UNFOLD_ALL
