from functools import partial

from typing import List, Any

from a_protocol_0.enums.Push2InstrumentModeEnum import Push2InstrumentModeEnum
from a_protocol_0.enums.Push2MainModeEnum import Push2MainModeEnum
from a_protocol_0.enums.Push2MatrixModeEnum import Push2MatrixModeEnum
from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
from a_protocol_0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from a_protocol_0.sequence.Sequence import Sequence


class AutomationMidiTrack(SimpleMidiTrack):
    CLIP_CLASS = AutomationMidiClip

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AutomationMidiTrack, self).__init__(*a, **k)
        # this works here because the tracks are built left to right
        self.clip_slots = self.clip_slots  # type: List[AutomationMidiClipSlot]
        self.push2_selected_main_mode = Push2MainModeEnum.CLIP
        self.push2_selected_matrix_mode = Push2MatrixModeEnum.NOTE
        self.push2_selected_instrument_mode = str(Push2InstrumentModeEnum.SPLIT_MELODIC_SEQUENCER)

    def _added_track_init(self):
        # type: () -> Sequence
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
