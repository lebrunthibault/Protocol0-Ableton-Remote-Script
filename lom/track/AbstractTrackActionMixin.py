from abc import abstractmethod
from typing import TYPE_CHECKING, Callable

import Live

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


# noinspection PyTypeHints
class AbstractTrackActionMixin(object):
    def action_arm(self):
        # type: (AbstractTrack) -> None
        if self.arm:
            return
        self.base_track.collapse_devices()
        if self.can_be_armed:
            self.song.unfocus_all_tracks()
            self.action_arm_track()
        elif self.is_foldable:
            self.is_folded = not self.is_folded

    @abstractmethod
    def action_arm_track(self):
        # type: (AbstractTrack) -> None
        pass

    def action_unarm(self):
        # type: (AbstractTrack) -> None
        self.color = self.base_color
        if self.is_foldable:
            self.base_track.is_folded = True
        [setattr(track, "arm", False) for track in self.all_tracks]
        [setattr(clip, "color", self.base_color) for clip in self.all_clips]
        self.action_unarm_track()

    def action_unarm_track(self):
        # type: (AbstractTrack) -> None
        pass

    def action_show_instrument(self):
        # type: (AbstractTrack) -> None
        if not self.instrument or not self.instrument.can_be_shown:
            return
        self.parent.application().view.show_view(u'Detail/DeviceChain')
        self.is_folded = False
        self.instrument.show_hide(force_show=self.song.selected_track != self.instrument.device_track)

    def action_solo(self):
        # type: (AbstractTrack) -> None
        self.base_track.solo = not self.base_track.solo

    @abstractmethod
    def action_switch_monitoring(self):
        # type: (AbstractTrack) -> None
        pass

    def action_restart_and_record(self, action_record_func, only_audio=False):
        # type: (AbstractTrack, Callable, bool) -> None
        """ restart audio to get a count in and recfix"""
        if not self.can_be_armed:
            return
        if self.is_recording:
            return self.action_undo()
        if self.song._song.session_record_status != Live.Song.SessionRecordStatus.off:
            return
        self.song._song.session_automation_record = True

        if not only_audio:
            self.song.stop_playing()
        action_record_func()

        self.parent.log_debug([t.is_hearable for t in self.song.tracks])
        if len(filter(None, [t.is_hearable for t in self.song.tracks])) <= 1 and not only_audio:
            self.song.metronome = True

        self.parent.wait_bars(self.bar_count + 1, self._post_record)

    def _post_record(self):
        # type: (AbstractTrack) -> None
        self.parent.log_debug("post rec")
        self.song.metronome = False
        track = self.midi if hasattr(self, "midi") else self
        track.has_monitor_in = False

    @abstractmethod
    def action_record_all(self):
        # type: () -> None
        """ this records normally on a simple track and both midi and audio on a group track """
        pass

    def action_record_audio_only(self):
        # type: (AbstractTrack) -> None
        """
            this records normally on a simple track and only audio on a group track
            is is available on other tracks just for ease of use
        """
        self.action_record_all()

    def stop(self):
        # type: (AbstractTrack) -> None
        self.base_track._track.stop_all_clips()

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

    def collapse_devices(self):
        # type: (AbstractTrack) -> None
        for device in self.all_devices:
            device.view.is_collapsed = not (
                    isinstance(device, Live.RackDevice.RackDevice) or self.parent.deviceManager.is_track_instrument(
                self, device))
