from functools import partial

import Live
from typing import TYPE_CHECKING, Any, Optional, NoReturn

from protocol0.config import Config
from protocol0.constants import QUANTIZATION_OPTIONS
from protocol0.devices.InstrumentSimpler import InstrumentSimpler
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import session_view_only, arrangement_view_only, crashes_ableton

if TYPE_CHECKING:
    from protocol0.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints,PyAttributeOutsideInit
class AbstractTrackActionMixin(object):
    # noinspection PyUnusedLocal
    def validate_configuration(self, log=True):
        # type: (AbstractTrack, bool) -> bool
        return True

    def fix_configuration(self):
        # type: (AbstractTrack) -> None
        return None

    def select(self):
        # type: (AbstractTrack) -> Sequence
        return self.song.select_track(self)

    def toggle_arm(self):
        # type: (AbstractTrack) -> None
        self.unarm() if self.is_armed else self.arm()

    def toggle_solo(self):
        # type: () -> None
        self.solo = not self.solo  # type: ignore[has-type]

    def toggle_mute(self):
        # type: () -> None
        self.mute = not self.mute  # type: ignore[has-type]

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
        assert self.instrument
        return len(
            self.clips) == 0 or not InterfaceState.PROTECTED_MODE_ACTIVE or not self.instrument.HAS_TOTAL_RECALL or isinstance(
            self.instrument,
            InstrumentSimpler)

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
        raise NotImplementedError()

    @session_view_only
    def session_record(self, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        if self.is_record_triggered:
            return self._cancel_record()
        self.pre_record(record_type=record_type)
        InterfaceState.CURRENT_RECORD_TYPE = record_type

        seq = Sequence()
        seq.add(partial(self._pre_session_record, record_type))

        if record_type == RecordTypeEnum.NORMAL:
            seq.add(self.session_record_all)
        elif record_type == RecordTypeEnum.AUDIO_ONLY:
            seq.add(self.session_record_audio_only)

        seq.add(partial(self.post_session_record, record_type))

        return seq.done()

    @arrangement_view_only
    def arrangement_record(self, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Sequence
        assert self.is_armed
        seq = Sequence()
        if self.song.record_mode:
            self.song.record_mode = False
            return seq.done()

        self.pre_record(record_type=record_type)

        self.has_monitor_in = False

        if record_type == RecordTypeEnum.NORMAL:
            seq.add(self.arrangement_record_all)
        elif record_type == RecordTypeEnum.AUDIO_ONLY:
            seq.add(self.arrangement_record_audio_only)
        seq.add(self.post_arrangement_record)
        return seq.done()

    def session_record_all(self):
        # type: (AbstractTrack) -> Sequence
        """ this records normally on a simple track and both midi and audio on a group track """
        raise NotImplementedError

    def session_record_audio_only(self):
        # type: (AbstractTrack) -> None
        """ overridden """
        raise NotImplementedError("session_record_audio_only not available on this track")

    def arrangement_record_all(self):
        # type: (AbstractTrack) -> Sequence
        return self.song.global_record()

    def arrangement_record_audio_only(self):
        # type: (AbstractTrack) -> None
        raise NotImplementedError("arrangement_record_audio_only not available on this track")

    def pre_record(self, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> None
        if record_type == RecordTypeEnum.NORMAL:
            if self.song.tempo < Config.SPLIT_QUANTIZATION_TEMPO:
                record_quantization_index = QUANTIZATION_OPTIONS.index(self.song.midi_recording_quantization)
                if record_quantization_index < QUANTIZATION_OPTIONS.index(
                        Live.Song.RecordingQuantization.rec_q_sixtenth):
                    self.parent.log_error(
                        "You're recording midi with a quantization of %s" % self.song.midi_recording_quantization)

    def _pre_session_record(self, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        """ restart audio to get a count in and recfix"""
        if not self.is_armed:
            self.parent.log_error("%s is not armed for recording" % self)
            return None

        self.song.record_mode = False
        self.song.stop_playing()
        self.song.session_automation_record = True

        if len(list(filter(None, [t.is_hearable for t in self.song.simple_tracks]))) <= 1:
            self.song.metronome = True

        seq = Sequence()
        if record_type == RecordTypeEnum.NORMAL and self.next_empty_clip_slot_index is None:
            seq.add(self.song.create_scene)
            seq.add(self.arm_track)
        return seq.done()

    def _cancel_record(self):
        # type: (AbstractTrack) -> Sequence
        self.parent.clear_tasks()
        seq = Sequence()
        if InterfaceState.CURRENT_RECORD_TYPE == RecordTypeEnum.NORMAL:
            seq.add(partial(self.delete_playable_clip))
        seq.add(self._delete_scene_if_empty)
        seq.add(partial(self.stop, immediate=True))
        seq.add(partial(self.post_session_record, InterfaceState.CURRENT_RECORD_TYPE))
        seq.add(self.song.stop_playing)
        return seq.done()

    @crashes_ableton
    def _delete_scene_if_empty(self):
        # type: (AbstractTrack) -> Sequence
        """ creates random crashes """
        seq = Sequence()
        if self.song.selected_scene.length == 0:
            seq.add(wait=1)
            seq.add(self.song.selected_scene.delete)
            seq.add(wait=1)
            seq.add(self.arm_track)
        return seq.done()

    def post_session_record(self, *_, **__):
        # type: (AbstractTrack, Any, Any) -> None
        """ overridden """
        self.song.metronome = False
        self.has_monitor_in = False
        self.song.session_automation_record = True
        clip = self.base_track.playable_clip
        if clip:
            clip.select()
            clip.clip_name.update(base_name="")
            clip.post_record()

    def post_arrangement_record(self):
        # type: (AbstractTrack) -> None
        self.song.stop_playing()
        self.has_monitor_in = False

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
        qz = self.song.clip_trigger_quantization
        if immediate:
            self.song.clip_trigger_quantization = 0
        self.base_track._track.stop_all_clips()
        if immediate:
            self.parent.defer(partial(setattr, self.song, "clip_trigger_quantization", qz))

    def load_device_from_enum(self, device_enum):
        # type: (AbstractTrack, DeviceEnum) -> Sequence
        seq = Sequence()
        seq.add(self.select)
        seq.add(partial(self.parent.browserManager.load_device_from_enum, device_enum))
        return seq.done()

    def refresh_appearance(self):
        # type: (AbstractTrack) -> None
        self.track_name.update()
        self.refresh_color()

    def refresh_color(self):
        # type: (AbstractTrack) -> None
        self.color = self.computed_color
        if self.group_track:
            self.group_track.refresh_color()
        from protocol0.lom.track.group_track.SimpleGroupTrack import SimpleGroupTrack

        if not isinstance(self, SimpleGroupTrack):
            for clip in self.clips:
                clip.color = self.computed_color

    def scroll_volume(self, go_next):
        # type: (AbstractTrack, bool) -> None
        abs_factor = 1.01
        factor = abs_factor if go_next else (1 / abs_factor)
        self.volume *= factor
