from functools import partial

import Live
from typing import TYPE_CHECKING, Any, Optional, NoReturn, Callable, cast

from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import retry
from protocol0.utils.utils import find_if

if TYPE_CHECKING:
    from protocol0.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints
class AbstractTrackActionMixin(object):
    @property
    def is_folded(self):
        # type: (AbstractTrack) -> bool
        return bool(self._track.fold_state) if self.is_foldable else True

    @is_folded.setter
    def is_folded(self, is_folded):
        # type: (AbstractTrack, bool) -> None
        if self.is_foldable:
            self._track.fold_state = int(is_folded)

    @property
    def solo(self):
        # type: (AbstractTrack) -> bool
        return self._track.solo

    @solo.setter
    def solo(self, solo):
        # type: (AbstractTrack, bool) -> None
        self._track.solo = solo

    @property
    def is_armed(self):
        # type: () -> bool
        return False

    @is_armed.setter
    def is_armed(self, is_armed):
        # type: (AbstractTrack, bool) -> None
        for track in self.active_tracks:
            track.is_armed = is_armed

    @property
    def has_monitor_in(self):
        # type: (AbstractTrack) -> bool
        return not self.is_foldable and self._track.current_monitoring_state == 0

    @has_monitor_in.setter
    def has_monitor_in(self, has_monitor_in):
        # type: (AbstractTrack, bool) -> None
        try:
            self._track.current_monitoring_state = int(not has_monitor_in)
        except RuntimeError:
            pass  # Live throws sometimes 'Master or sendtracks have no monitoring state!'

    def select(self):
        # type: (AbstractTrack) -> None
        self.song.select_track(self)

    def toggle_arm(self):
        # type: (AbstractTrack) -> None
        self.unarm() if self.is_armed else self.arm()

    def toggle_solo(self):
        # type: () -> None
        self.solo = not self.solo  # type: ignore[has-type]

    def arm(self):
        # type: (AbstractTrack) -> Optional[Sequence]
        if self.is_armed:
            return None
        self.song.unfocus_all_tracks()
        return self.arm_track()

    def arm_track(self):
        # type: () -> Optional[Sequence]
        raise NotImplementedError()

    def unarm(self):
        # type: (AbstractTrack) -> None
        if not self.is_armed:
            return
        self.is_armed = False
        self.unarm_track()
        # self.refresh_color()

    def unarm_track(self):
        # type: (AbstractTrack) -> None
        pass

    def show_hide_instrument(self):
        # type: (AbstractTrack) -> None
        if not self.instrument or not self.instrument.CAN_BE_SHOWN:
            return None
        self.is_folded = False
        self.instrument.show_hide()

    def scroll_presets_or_samples(self, go_next):
        # type: (AbstractTrack, bool) -> None
        if self.instrument:
            if len(self.clips) and InterfaceState.PROTECTED_MODE_ACTIVE:
                self.parent.show_message("Cannot change preset when a clip is already recorded")
            else:
                self.instrument.scroll_presets_or_samples(go_next)

    def scroll_preset_categories(self, go_next):
        # type: (AbstractTrack, bool) -> None
        if self.instrument:
            if len(self.clips) and InterfaceState.PROTECTED_MODE_ACTIVE:
                self.parent.show_message("Cannot change preset category when a clip is already recorded")
            else:
                self.instrument.scroll_preset_categories(go_next=go_next)

    def switch_monitoring(self):
        # type: (AbstractTrack) -> NoReturn
        raise NotImplementedError()

    def create_scene_if_needed(self):
        # type: (AbstractTrack) -> None
        if not self.next_empty_clip_slot_index:
            self.song.create_scene()

    def record(self, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        """ restart audio to get a count in and recfix"""
        if not self.can_be_armed:
            return None
        if self.song.session_record_status == Live.Song.SessionRecordStatus.transition:  # record count in
            self.parent.clear_tasks()
            self.stop(immediate=True)
            self.post_record()
            return None
        elif self.song.session_record_status == Live.Song.SessionRecordStatus.on:  # in recording
            self.parent.clear_tasks()
            seq = Sequence()
            seq.add(self.in_record)
            seq.add(self.post_record)
            return seq.done()

        self.song.session_record = True

        self.song.stop_playing()

        if len(list(filter(None, [t.is_hearable for t in self.song.simple_tracks]))) <= 1:
            self.song.metronome = True

        seq = Sequence()
        if not self.is_armed:
            seq.add(self.arm, silent=True)
        if record_type == RecordTypeEnum.NORMAL and self.next_empty_clip_slot_index is None:
            seq.add(self.song.create_scene)
            seq.add(partial(self.record, record_type))
            return seq.done()

        if record_type == RecordTypeEnum.MULTIPLE:
            seq.add(cast(Callable[..., Any], self.record_multiple))
            return seq.done()

        if record_type == RecordTypeEnum.NORMAL:
            seq.add(cast(Callable[..., Any], self.record_all))
        elif record_type == RecordTypeEnum.AUDIO_ONLY:
            seq.add(cast(Callable[..., Any], self.record_audio_only))
        seq.add(self.post_record)

        return seq.done()

    def record_all(self):
        # type: (AbstractTrack) -> Sequence
        """ this records normally on a simple track and both midi and audio on a group track """
        raise NotImplementedError

    def record_audio_only(self, *a, **k):
        # type: (AbstractTrack, Any, Any) -> Sequence
        """
        overridden
        this records normally on a simple track and only audio on a group track
        is is available on other tracks just for ease of use
        """
        return self.record_all()

    def record_multiple(self):
        # type: (AbstractTrack) -> Sequence
        seq = Sequence()
        seq.add(complete_on=self._has_clip_listener)
        self.record_all()
        seq.add(partial(self.parent.wait_beats, 1, self.create_scene_if_needed))
        seq.add(partial(self.parent.wait_bars, InterfaceState.SELECTED_RECORDING_BAR_LENGTH, self.record_multiple))
        return seq.done()

    def in_record(self):
        # type: (AbstractTrack) -> None
        """ happens when the rec button is clicked during a recording. Overridden """
        raise NotImplementedError

    def post_record(self):
        # type: (AbstractTrack) -> None
        " overridden "
        self.song.metronome = False
        self.has_monitor_in = False
        self.song.session_record = False
        if self.base_track.playable_clip:
            self.base_track.playable_clip.select()
            if self.base_track.playable_clip.is_midi:
                self.base_track.playable_clip.show_loop()
                self.base_track.playable_clip.quantize()

    def play_stop(self):
        # type: (AbstractTrack) -> None
        self.stop() if self.is_playing else self.play()

    def play(self):
        # type: (AbstractTrack) -> None
        from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack

        if self.is_foldable:
            for sub_track in self.sub_tracks:
                sub_track.play()
        elif isinstance(self, SimpleTrack) and self.playable_clip:
            self.playable_clip.fire()
            if not self.playable_clip.is_recording:
                self.playable_clip.start_marker = self.song.selected_scene.playing_position

    def stop(self, immediate=False):
        # type: (AbstractTrack, bool) -> None
        qz = self.song.clip_trigger_quantization
        if immediate:
            self.song.clip_trigger_quantization = 0
        self.base_track._track.stop_all_clips()
        if immediate:
            self.parent.defer(partial(setattr, self.song, "clip_trigger_quantization", qz))

    def undo(self):
        # type: (AbstractTrack) -> None
        self.parent.clear_tasks()
        self.undo_track()

    def undo_track(self):
        # type: () -> NoReturn
        raise NotImplementedError()

    def reset_track(self):
        # type: (AbstractTrack) -> None
        self.solo = False
        if self.is_armed:
            self.unarm()

    def load_any_device(self, device_type, device_name):
        # type: (AbstractTrack, str, str) -> Sequence
        seq = Sequence()
        seq.add(self.select)
        seq.add(partial(self.parent.browserManager.load_any_device, device_type, device_name))
        return seq.done()

    @retry(3, 8)
    def set_output_routing_to(self, track):
        # type: (AbstractTrack, AbstractTrack) -> None
        if track is None:
            raise Protocol0Error("You passed None to %s" % self.set_output_routing_to.__name__)

        from protocol0.lom.track.AbstractTrack import AbstractTrack

        track = track._track if isinstance(track, AbstractTrack) else track
        output_routing_type = find_if(lambda r: r.attached_object == track, self.available_output_routing_types)

        if not output_routing_type:
            output_routing_type = find_if(
                lambda r: r.display_name.lower() == track.name.lower(), self.available_output_routing_types
            )

        if not output_routing_type:
            raise Protocol0Error("Couldn't find the output routing type of the given track")

        if self.output_routing_type != output_routing_type:
            self.output_routing_type = output_routing_type

    def set_input_routing_type(self, track):
        # type: (AbstractTrack, Any) -> None
        from protocol0.lom.track.AbstractTrack import AbstractTrack

        track = track._track if isinstance(track, AbstractTrack) else track

        if track is None:
            self.input_routing_type = self.available_input_routing_types[-1]  # No input
            return None

        input_routing_type = find_if(lambda r: r.attached_object == track, self.available_input_routing_types)
        if not input_routing_type:
            input_routing_type = find_if(
                lambda r: r.display_name.lower() == track.name.lower(), self.available_input_routing_types
            )

        if not input_routing_type:
            raise Protocol0Error("Couldn't find the input routing type of the given track")

        if self.input_routing_type != input_routing_type:
            self.input_routing_type = input_routing_type

    def refresh_appearance(self):
        # type: (AbstractTrack) -> None
        self.track_name.update()
        self.refresh_color()

    def refresh_color(self):
        # type: (AbstractTrack) -> None
        if self.abstract_group_track:
            return  # not allowed when the track is managed
        self.color = self.computed_color
        if self.group_track:
            self.group_track.refresh_color()
        from protocol0.lom.track.group_track.SimpleGroupTrack import SimpleGroupTrack

        if not isinstance(self, SimpleGroupTrack):
            for clip in self.clips:
                clip.color = self.computed_color
