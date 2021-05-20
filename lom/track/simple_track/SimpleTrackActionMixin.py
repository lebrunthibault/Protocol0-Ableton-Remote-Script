from functools import partial
from itertools import chain, imap  # type: ignore[attr-defined]

from typing import Optional, List, Union
from typing import TYPE_CHECKING

from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.device.DeviceChain import DeviceChain
from a_protocol_0.lom.device.RackDevice import RackDevice
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import scroll_values, find_if

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints
class SimpleTrackActionMixin(object):
    @property
    def is_armed(self):
        # type: (SimpleTrack) -> bool
        return self.can_be_armed and self._track.arm

    @is_armed.setter
    def is_armed(self, is_armed):
        # type: (SimpleTrack, bool) -> None
        if self.can_be_armed:
            self._track.arm = is_armed

    @property
    def is_armable(self):
        # type: (SimpleTrack) -> bool
        """ Checks for disabled input routing """
        if not self.can_be_armed:
            return True
        self.is_armed = True
        if self.is_armed:
            self.is_armed = False
            return True
        else:
            return False

    def arm_track(self):
        # type: (SimpleTrack) -> Optional[Sequence]
        if self.is_foldable:
            self.is_folded = not self.is_folded  # type: ignore[has-type]
        else:
            self.mute = False
            self.is_armed = True

        seq = Sequence()

        if self.instrument:
            seq.add(self.instrument.check_activated)
            seq.add(wait=5)
            seq.add(self.parent.keyboardShortcutManager.hide_plugins)

        return seq.done()

    def switch_monitoring(self):
        # type: (SimpleTrack) -> None
        self.has_monitor_in = not self.has_monitor_in  # type: ignore[has-type]

    def undo_track(self):
        # type: (SimpleTrack) -> None
        if self.is_recording:
            self.song.metronome = False
            self.playable_clip.delete()
        elif self.is_triggered:
            self.stop()
        else:
            self.song.undo()

    def record_all(self):
        # type: (SimpleTrack) -> Sequence
        """ finishes on end of recording """
        seq = Sequence()
        assert self.next_empty_clip_slot_index is not None
        seq.add(self.clip_slots[self.next_empty_clip_slot_index].record)  # type: ignore[has-type]
        return seq.done()

    def in_record(self):
        # type: (SimpleTrack) -> Sequence
        assert self.playable_clip
        seq = Sequence()
        seq.add(self.play, complete_on=self.playable_clip._is_recording_listener)
        seq.add(self.playable_clip.decrement_bar_length)
        return seq.done()

    def scroll_clips(self, go_next):
        # type: (SimpleTrack, bool) -> None
        self.parent.navigationManager.show_clip_view()
        if len(self.clips) == 0:
            return
        if self.song.highlighted_clip_slot == self.clips[0] and not go_next:
            return self.parent.keyboardShortcutManager.up()

        if self.song.selected_clip or self.playable_clip:
            self.song.selected_clip = scroll_values(self.clips, self.song.selected_clip or self.playable_clip, go_next)

    def has_device(self, device_name):
        # type: (SimpleTrack, str) -> bool
        return find_if(lambda d: d.name == device_name, self.base_track.all_devices) is not None

    def find_all_devices(self, track_or_chain, only_visible=False):
        # type: (SimpleTrack, Optional[Union[SimpleTrack, DeviceChain]], bool) -> List[Device]
        u""" Returns a list with all devices from a track or chain """
        devices = []
        if track_or_chain is None:
            return []
        for device in filter(None, track_or_chain.devices):  # type: Device
            if not isinstance(device, RackDevice):
                devices += [device]
                continue

            if device.can_have_drum_pads and device.can_have_chains:
                devices += chain([device], self.find_all_devices(device.selected_chain))
            elif not device.can_have_drum_pads and isinstance(device, RackDevice):
                devices += chain(
                    [device],
                    *imap(
                        partial(self.find_all_devices, only_visible=only_visible),
                        filter(None, device.chains),
                    )
                )
        return devices
