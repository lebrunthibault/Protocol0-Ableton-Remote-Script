from functools import partial

from typing import List, TYPE_CHECKING

from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.AbstractAutomationTrack import AbstractAutomationTrack
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack


class AutomationMidiTrack(AbstractAutomationTrack):
    CLIP_CLASS = AutomationMidiClip

    def __init__(self, *a, **k):
        # type: (DeviceParameter) -> None
        super(AutomationMidiTrack, self).__init__(*a, **k)
        # this works here because the tracks are built left to right
        self.linked_track = None  # type: AutomationAudioTrack

        self.clip_slots = self.clip_slots  # type: List[AutomationMidiClipSlot]
        self.push2_selected_main_mode = "clip"
        self.push2_selected_matrix_mode = "note"
        self.push2_selected_instrument_mode = "split_melodic_sequencer"

    def _added_track_init(self):
        """ when this is called the AutomatedTrack and AutomationAudioTrack are fully loaded """
        self.clear_devices()
        seq = Sequence()
        seq.add(partial(self._create_base_clip, clip_slot_index=self.song.selected_scene.index))

        return seq.done()

    def _create_base_clip(self, clip_slot_index):
        # type: (int) -> Sequence
        seq = Sequence()
        seq.add(partial(self.create_clip, clip_slot_index=clip_slot_index, bar_count=1))
        return seq.done()
