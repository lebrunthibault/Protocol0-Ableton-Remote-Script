from functools import partial

from typing import TYPE_CHECKING, Any, Optional, NoReturn

from protocol0.components.TrackDataManager import save_track_data
from protocol0.config import Config
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints,PyAttributeOutsideInit
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

    def toggle_mute(self):
        # type: () -> None
        self.mute = not self.mute  # type: ignore[has-type]

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

    @property
    def can_change_presets(self):
        # type: (AbstractTrack) -> bool
        """ overridden """
        return True

    def scroll_presets_or_samples(self, go_next):
        # type: (AbstractTrack, bool) -> None
        if self.instrument:
            if not self.can_change_presets:
                self.parent.show_message("Cannot change preset when a clip is already recorded")
            else:
                self.instrument.scroll_presets_or_samples(go_next)

    def scroll_preset_categories(self, go_next):
        # type: (AbstractTrack, bool) -> None
        if self.instrument:
            if not self.can_change_presets:
                self.parent.show_message("Cannot change preset category when a clip is already recorded")
            else:
                self.instrument.scroll_preset_categories(go_next=go_next)

    def switch_monitoring(self):
        # type: (AbstractTrack) -> NoReturn
        self.parent.show_message("%s cannot switch monitoring" % self)

    def record(self, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        seq = Sequence()
        if not self.is_armed:
            if len(list(self.song.armed_tracks)) != 0:
                self.system.show_warning("The current track is not armed and other tracks are armed")
                return None
            else:
                seq.add(self.arm)

        seq.add(self.song.check_midi_recording_quantization)

        if self.application.session_view_active:
            seq.add(partial(self.session_record, record_type=record_type))
        else:
            seq.add(partial(self.arrangement_record, record_type=record_type))
        return seq.done()

    def session_record(self, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        if self.is_record_triggered and Config.CURRENT_RECORD_TYPE is not None:
            return self._cancel_record()
        Config.CURRENT_RECORD_TYPE = record_type

        seq = Sequence()
        seq.add(partial(self._pre_session_record, record_type))
        seq.add(partial(self._launch_count_in, record_type))

        if record_type == RecordTypeEnum.NORMAL:
            seq.add(self._session_record_all)
        elif record_type == RecordTypeEnum.AUDIO_ONLY:
            seq.add(self._session_record_audio_only)

        seq.add(partial(self.post_session_record, record_type))

        return seq.done()

    def arrangement_record(self, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Sequence
        assert self.is_armed
        seq = Sequence()
        if self.song.record_mode:
            self.song.record_mode = False
            return seq.done()

        self.has_monitor_in = False

        if record_type == RecordTypeEnum.NORMAL:
            seq.add(self.arrangement_record_all)
        elif record_type == RecordTypeEnum.AUDIO_ONLY:
            seq.add(self.arrangement_record_audio_only)
        seq.add(self.post_arrangement_record)
        return seq.done()

    def _session_record_all(self):
        # type: (AbstractTrack) -> Sequence
        """ this records normally on a simple track and both midi and audio on a group track """
        raise NotImplementedError

    def _session_record_audio_only(self):
        # type: (AbstractTrack) -> None
        """ overridden """
        self.parent.log_error("session_record_audio_only not available on this track")
        return None

    def arrangement_record_all(self):
        # type: (AbstractTrack) -> Sequence
        return self.song.global_record()

    def arrangement_record_audio_only(self):
        # type: (AbstractTrack) -> None
        self.parent.log_error("arrangement_record_audio_only not available on this track")
        return None

    def _pre_session_record(self, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        """ restart audio to get a count in and recfix"""
        if not self.is_armed:
            self.parent.log_error("%s is not armed for recording" % self)
            return None

        self.song.record_mode = False
        self.song.session_automation_record = True

        seq = Sequence()
        if record_type == RecordTypeEnum.NORMAL:
            if self.next_empty_clip_slot_index is None:
                seq.add(self.song.create_scene)
                seq.add(self.arm_track)
                seq.add(partial(self._pre_session_record, record_type))
            elif self.next_empty_clip_slot_index != self.song.selected_scene.index:
                seq.add(self.song.scenes[self.next_empty_clip_slot_index].select)

        return seq.done()

    def _launch_count_in(self, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        self.song.metronome = True

        if record_type == RecordTypeEnum.AUDIO_ONLY:
            return None

        # solo for count in
        self.solo = True
        self.parent.wait_bars(1, partial(setattr, self, "solo", False))

        self.song.stop_playing()
        assert self.next_empty_clip_slot_index is not None
        recording_scene = self.song.scenes[self.next_empty_clip_slot_index]
        self.song.stop_all_clips(quantized=False)  # stopping previous scene clips

        self.song.is_playing = True

        if recording_scene.length:
            seq = Sequence()
            seq.add(wait=1)
            seq.add(recording_scene.fire)
            return seq.done()
        else:
            return None

    def _cancel_record(self):
        # type: (AbstractTrack) -> Sequence
        self.parent.clear_tasks()
        seq = Sequence()
        seq.add(partial(self.delete_playable_clip))
        seq.add(partial(self.stop, immediate=True))
        seq.add(partial(self.post_session_record, Config.CURRENT_RECORD_TYPE))
        seq.add(self.song.stop_playing)
        return seq.done()

    def post_session_record(self, update_clip_name=True, *_, **__):
        # type: (AbstractTrack, bool, Any, Any) -> None
        """ overridden """
        self.song.metronome = False
        self.has_monitor_in = False
        self.solo = False
        self.song.session_automation_record = True
        Config.CURRENT_RECORD_TYPE = None
        # if self.song.selected_scene.length == 0:
        #     self.parent.defer(self.song.selected_scene.delete)
        clip = self.base_track.playable_clip
        if clip:
            clip.select()
            if update_clip_name:
                clip.clip_name.update(base_name="")  # type: ignore[has-type]
            clip.post_record()

    def post_arrangement_record(self):
        # type: (AbstractTrack) -> None
        self.song.stop_playing()
        self.has_monitor_in = False

    @save_track_data
    def toggle_record_clip_tails(self):
        # type: (AbstractTrack) -> None
        from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
        if not isinstance(self, ExternalSynthTrack):
            self.parent.show_message("Recording clip tails is available only on an ExternalSynthTrack")
            return None

        if not self.audio_tail_track:
            self.system.show_warning("Please create a clip tail track")
            return None

        self.record_clip_tails = not self.record_clip_tails
        self.parent.show_message("Record clip tails %s" % ("ON" if self.record_clip_tails else "OFF"))

    def delete_playable_clip(self):
        # type: (AbstractTrack) -> Sequence
        """ overridden """
        seq = Sequence()
        if self.base_track.playable_clip:
            seq.add(self.base_track.playable_clip.delete)
        return seq.done()

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
        if immediate:
            self.song.disable_clip_trigger_quantization()
        self.base_track._track.stop_all_clips()
        if immediate:
            self.song.enable_clip_trigger_quantization()

    def load_device_from_enum(self, device_enum):
        # type: (AbstractTrack, DeviceEnum) -> Sequence
        seq = Sequence()
        seq.add(self.select)
        seq.add(partial(self.parent.browserManager.load_device_from_enum, device_enum))
        return seq.done()

    def refresh_appearance(self):
        # type: (AbstractTrack) -> None
        if not self.base_track.IS_ACTIVE:
            return

        self.track_name.update()
        self.refresh_color()

    def refresh_color(self):
        # type: (AbstractTrack) -> None
        self.color = self.computed_color

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
