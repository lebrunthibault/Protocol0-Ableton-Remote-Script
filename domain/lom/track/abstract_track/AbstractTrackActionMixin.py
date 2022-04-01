from typing import TYPE_CHECKING, Optional, List, cast

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack  # noqa


# noinspection PyTypeHints,PyAttributeOutsideInit,DuplicatedCode
class AbstractTrackActionMixin(object):
    def matches_name(self, name):
        # type: (AbstractTrack, str) -> bool
        return self.name.lower().strip() == name.lower().strip()

    # noinspection PyUnusedLocal
    def select(self):
        # type: (AbstractTrack) -> Sequence
        return self._song.select_track(self)

    def duplicate(self):
        # type: (AbstractTrack) -> Sequence
        return self._song.duplicate_track(self.index)

    def delete(self):
        # type: (AbstractTrack) -> Sequence
        return self._song.delete_track(self.index)

    def toggle_arm(self):
        # type: (AbstractTrack) -> Optional[Sequence]
        if not SongFacade.selected_track().IS_ACTIVE:
            return None
        if self.is_armed:
            self.unarm()
            return None
        else:
            return self.arm()

    def fold(self):
        # type: (AbstractTrack) -> None
        if self.is_foldable:
            self.is_folded = True

    def arm(self):
        # type: (AbstractTrack) -> Optional[Sequence]
        if self.is_armed:
            return None
        self._song.unfocus_all_tracks()
        if self.is_foldable:
            self.is_folded = False
        return self.arm_track()

    def arm_track(self):
        # type: (AbstractTrack) -> Optional[Sequence]
        raise Protocol0Warning("Tried arming unarmable %s" % self)

    def unarm(self):
        # type: (AbstractTrack) -> None
        self.is_armed = False

    def stop(self, immediate=False):
        # type: (AbstractTrack, bool) -> None
        if immediate:
            self._song.disable_clip_trigger_quantization()
        self.base_track._track.stop_all_clips()
        if immediate:
            self._song.enable_clip_trigger_quantization()

    def refresh_appearance(self):
        # type: (AbstractTrack) -> None
        if not self.base_track.IS_ACTIVE:
            return
        self.track_name.update()
        self.refresh_color()

    def refresh_color(self):
        # type: (AbstractTrack) -> None
        self.color = self.computed_color
        for clip in self.clips:
            clip.color = self.color

    def scroll_volume(self, go_next):
        # type: (AbstractTrack, bool) -> None
        self.volume += 0.5 if go_next else -0.5

    def get_all_simple_sub_tracks(self):
        # type: (AbstractTrack) -> List[SimpleTrack]
        from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack  # noqa

        sub_tracks = []
        for sub_track in self.sub_tracks:
            if sub_track.is_foldable:
                sub_tracks += sub_track.get_all_simple_sub_tracks()
            else:
                sub_tracks.append(sub_track)

        return cast(List[SimpleTrack], sub_tracks)

    def add_or_replace_sub_track(self, sub_track, previous_sub_track=None):
        # type: (AbstractTrack, AbstractTrack, Optional[AbstractTrack]) -> None
        if sub_track in self.sub_tracks:
            return

        if previous_sub_track is None or previous_sub_track not in self.sub_tracks:
            self.sub_tracks.append(sub_track)
        else:
            sub_track_index = self.sub_tracks.index(previous_sub_track)
            self.sub_tracks[sub_track_index] = sub_track
