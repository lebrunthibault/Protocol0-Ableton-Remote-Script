from abc import abstractmethod
from functools import partial

import Live
from typing import TYPE_CHECKING, Callable, Any, Optional

from _Framework.Util import find_if
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.clip.AudioClip import AudioClip
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import retry

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints
class AbstractTrackActionMixin(object):
    def select(self):
        # type: (AbstractTrack) -> None
        return self.song.select_track(self)

    def action_arm(self):
        # type: (AbstractTrack) -> Optional[Sequence]
        if self.arm:
            return
        self.base_track.collapse_devices()
        self.song.unfocus_all_tracks()
        return self.action_arm_track()

    @abstractmethod
    def action_arm_track(self):
        # type: (AbstractTrack) -> None
        pass

    def action_unarm(self):
        # type: (AbstractTrack) -> None
        self.color = self.base_color
        [setattr(track, "arm", False) for track in self.all_tracks]
        [setattr(clip, "color", self.base_color) for clip in self.all_clips]
        self.action_unarm_track()

    def action_unarm_track(self):
        # type: (AbstractTrack) -> None
        pass

    def action_show_hide_instrument(self):
        # type: (AbstractTrack) -> None
        if not self.instrument:
            self.instrument_track.instrument = self.parent.deviceManager.make_instrument_from_simple_track(
                track=self.instrument_track)

        if not self.instrument or not self.instrument.can_be_shown:
            return
        self.parent.clyphxNavigationManager.show_track_view()
        self.is_folded = False
        self.instrument.show_hide()

    def action_solo(self):
        # type: (AbstractTrack) -> None
        self.base_track.solo = not self.base_track.solo

    @abstractmethod
    def action_switch_monitoring(self):
        # type: (AbstractTrack) -> None
        pass

    def action_restart_and_record(self, action_record_func):
        # type: (AbstractTrack, Callable) -> None
        """ restart audio to get a count in and recfix"""
        if not self.can_be_armed:
            return
        if self.is_recording:
            return self.action_undo()
        if self.song._song.session_record_status != Live.Song.SessionRecordStatus.off:
            return
        self.song._song.session_automation_record = True

        self.song.stop_playing()

        if len(filter(None, [t.is_hearable for t in self.song.simple_tracks])) <= 1:
            self.song.metronome = True

        seq = Sequence()
        if self.next_empty_clip_slot_index is None:
            seq.add(self.song.create_scene)
            # here the tracks are mapped again ! we cannot simply call this method again on a stale object
            seq.add(self.parent.current_action)
        else:
            seq.add(action_record_func)

        return seq.done()

    def _post_record(self, *a, **k):
        # type: (AbstractTrack, Any, Any) -> None
        " overridden "
        self.song.metronome = False
        self.has_monitor_in = False
        clip = self.base_track.playable_clip  # type: AudioClip
        if self.is_audio:
            clip.warp_mode = Live.Clip.WarpMode.complex_pro
        self.base_track.playable_clip.select()

    @abstractmethod
    def action_record_all(self):
        # type: () -> Sequence
        """ this records normally on a simple track and both midi and audio on a group track """
        raise NotImplementedError

    def action_record_audio_only(self, *a, **k):
        # type: (AbstractTrack) -> None
        """
            overridden
            this records normally on a simple track and only audio on a group track
            is is available on other tracks just for ease of use
        """
        return self.action_record_all()

    def play(self):
        # type: (AbstractTrack) -> None
        from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack

        if not self.song.is_playing:
            self.song.is_playing = True
        if self.is_foldable:
            [sub_track.play() for sub_track in self.sub_tracks]
        elif isinstance(self, SimpleTrack) and self.playable_clip:
            self.playable_clip.is_playing = True
            playing_position = 0
            if self.song.playing_clips:
                playing_position = max(self.song.playing_clips, key=lambda c: c.length).playing_position
            self.playable_clip.start_marker = self.parent.utilsManager.get_next_quantized_position(playing_position,
                                                                                                   self.playable_clip.length)

    def stop(self, immediate=False):
        # type: (AbstractTrack, bool) -> None
        qz = self.song.clip_trigger_quantization
        if immediate:
            self.song.clip_trigger_quantization = 0
        self.base_track._track.stop_all_clips()
        if immediate:
            self.parent.defer(partial(setattr, self.song, "clip_trigger_quantization", qz))

    def action_undo(self):
        # type: (AbstractTrack) -> None
        self.parent.clear_tasks()
        self.action_undo_track()

    @abstractmethod
    def action_undo_track(self):
        # type: (AbstractTrack) -> None
        pass

    def reset_track(self):
        # type: (AbstractTrack) -> None
        self.solo = False
        self.action_unarm()
        self.collapse_devices()

    def load_any_device(self, device_type, device_name):
        # type: (AbstractTrack, str, str) -> None
        seq = Sequence()
        seq.add(self.select)
        seq.add(partial(self.parent.browserManager.load_any_device, device_type, device_name))
        return seq.done()

    def collapse_devices(self):
        # type: (AbstractTrack) -> None
        for device in self.all_devices:
            device.is_collapsed = not (
                        isinstance(device, RackDevice) or self.parent.deviceManager.is_track_instrument(
                    self, device))

    @retry(2, 2)
    def set_output_routing_to(self, track):
        # type: (AbstractTrack, AbstractTrack) -> None
        if track is None:
            raise Protocol0Error("You passed None to %s" % self.set_output_routing_to.__name__)

        from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
        track = track._track if isinstance(track, AbstractTrack) else track
        output_routing_type = find_if(lambda r: r.attached_object == track,
                                      self.available_output_routing_types)

        if not output_routing_type:
            output_routing_type = find_if(lambda r: r.display_name.lower() == track.name.lower(),
                                          self.available_output_routing_types)

        if not output_routing_type:
            raise Protocol0Error("Couldn't find the output routing type of the given track")

        if self.output_routing_type != output_routing_type:
            self.output_routing_type = output_routing_type

    def set_input_routing_type(self, track):
        # type: (AbstractTrack, Any) -> None
        from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
        track = track._track if isinstance(track, AbstractTrack) else track

        if track is None:
            self.input_routing_type = self.available_input_routing_types[-1]  # No input
            return

        input_routing_type = find_if(lambda r: r.attached_object == track,
                                     self.available_input_routing_types)
        if not input_routing_type:
            input_routing_type = find_if(lambda r: r.display_name.lower() == track.name.lower(),
                                         self.available_input_routing_types)

        if not input_routing_type:
            raise Protocol0Error("Couldn't find the input routing type of the given track")

        if self.input_routing_type != input_routing_type:
            self.input_routing_type = input_routing_type
