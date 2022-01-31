from typing import TYPE_CHECKING, Any, Optional

from protocol0.domain.errors.InvalidTrackError import InvalidTrackError
from protocol0.domain.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints,PyAttributeOutsideInit,DuplicatedCode
class AbstractTrackActionMixin(object):
    # noinspection PyUnusedLocal
    def select(self):
        # type: (AbstractTrack) -> Sequence
        return self.song.select_track(self)

    def duplicate(self):
        # type: (AbstractTrack) -> Sequence
        return self.song.duplicate_track(self.index)

    def delete(self):
        # type: (AbstractTrack) -> Sequence
        return self.song.delete_track(self.index)

    def toggle_arm(self):
        # type: (AbstractTrack) -> None
        if not self.song.selected_track.IS_ACTIVE:
            return None
        self.unarm() if self.is_armed else self.arm()

    def toggle_fold(self):
        # type: (AbstractTrack) -> Optional[Sequence]
        if self.is_foldable:
            self.is_folded = not self.is_folded
            if not self.is_folded:
                return self.sub_tracks[0].select()
            else:
                return None

        if self.group_track:
            return self.group_track.toggle_fold()
        else:
            return None

    def toggle_solo(self):
        # type: () -> None
        self.solo = not self.solo  # type: ignore[has-type]

    def arm(self):
        # type: (AbstractTrack) -> Optional[Sequence]
        if self.is_foldable:
            self.is_folded = False
        if not self.is_armed:
            self.song.unfocus_all_tracks()
        return self.arm_track()

    def arm_track(self):
        # type: (AbstractTrack) -> Optional[Sequence]
        self.parent.log_warning("Tried arming unarmable %s" % self)
        return None

    def unarm(self):
        # type: (AbstractTrack) -> None
        self.is_armed = False
        self.unarm_track()

    def unarm_track(self):
        # type: (AbstractTrack) -> None
        pass

    def show_hide_instrument(self):
        # type: (AbstractTrack) -> None
        if not self.instrument or not self.instrument.CAN_BE_SHOWN:
            return None
        self.instrument.show_hide()

    def activate_instrument_plugin_window(self):
        # type: (AbstractTrack) -> None
        if not self.instrument or not self.instrument.CAN_BE_SHOWN:
            return None
        self.instrument.activate_plugin_window(force_activate=True)

    def scroll_presets_or_samples(self, go_next):
        # type: (AbstractTrack, bool) -> Sequence
        if self.instrument:
            return self.instrument.scroll_presets_or_samples(go_next)
        else:
            raise InvalidTrackError("Cannot scroll presets without an instrument")

    def scroll_preset_categories(self, go_next):
        # type: (AbstractTrack, bool) -> None
        if self.instrument:
            return self.instrument.scroll_preset_categories(go_next=go_next)
        else:
            raise InvalidTrackError("Cannot scroll categories without an instrument")

    def stop(self, immediate=False):
        # type: (AbstractTrack, bool) -> None
        if immediate:
            self.song.disable_clip_trigger_quantization()
        self.base_track._track.stop_all_clips()
        if immediate:
            self.song.enable_clip_trigger_quantization()

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
        abs_factor = 1.01
        factor = abs_factor if go_next else (1 / abs_factor)
        self.volume *= factor

    def get_data(self, key, default_value=None):
        # type: (AbstractTrack, str, Any) -> Any
        return self._track.get_data(key, default_value)

    def set_data(self, key, value):
        # type: (AbstractTrack, str, Any) -> None
        self._track.set_data(key, value)
