from functools import partial
from itertools import chain, imap  # type: ignore[attr-defined]

from typing import Optional, List, Union
from typing import TYPE_CHECKING

from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.device.Device import Device
from protocol0.lom.device.DeviceChain import DeviceChain
from protocol0.lom.device.RackDevice import RackDevice
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.utils import find_if

if TYPE_CHECKING:
    from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack


# noinspection PyTypeHints,PyArgumentList
class SimpleTrackActionMixin(object):
    def arm_track(self):
        # type: (SimpleTrack) -> Optional[Sequence]
        if self.is_foldable:
            self.is_folded = not self.is_folded  # type: ignore[has-type]
        else:
            self.mute = False
            self.is_armed = True

        seq = Sequence()

        if self.instrument:
            if self.instrument.needs_activation:
                seq.add(partial(self.instrument.activate_plugin_window))

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

    def delete_device(self, device):
        # type: (SimpleTrack, Device) -> Sequence
        seq = Sequence()
        if device not in self.devices:
            return seq.done()

        device_index = self.devices.index(device)
        self._track.delete_device(device_index)
        return seq.done()

    def session_record_all(self):
        # type: (SimpleTrack) -> Sequence
        """ finishes on end of recording """
        seq = Sequence()
        assert self.next_empty_clip_slot_index is not None
        recording_clip_slot = self.clip_slots[self.next_empty_clip_slot_index]
        recording_bar_length = InterfaceState.SELECTED_RECORDING_BAR_LENGTH.int_value
        seq.add(partial(recording_clip_slot.record, bar_length=recording_bar_length, bar_tail_length=0))
        return seq.done()

    def get_device_from_enum(self, device_enum):
        # type: (SimpleTrack, DeviceEnum) -> Optional[Device]
        return find_if(lambda d: d.name == device_enum.device_name, self.base_track.all_devices)

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
