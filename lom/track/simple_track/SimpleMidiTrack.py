from functools import partial

from typing import Any, List

from protocol0.enums.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.enums.Push2InstrumentModeEnum import Push2InstrumentModeEnum
from protocol0.enums.Push2MatrixModeEnum import Push2MatrixModeEnum
from protocol0.lom.clip.MidiClip import MidiClip
from protocol0.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence


class SimpleMidiTrack(SimpleTrack):
    DEFAULT_NAME = "midi"
    CLIP_SLOT_CLASS = MidiClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleMidiTrack, self).__init__(*a, **k)
        self.clip_slots = self.clip_slots  # type: List[MidiClipSlot]

        self.push2_selected_matrix_mode = Push2MatrixModeEnum.NOTE
        self.push2_selected_instrument_mode = Push2InstrumentModeEnum.SPLIT_MELODIC_SEQUENCER

    @property
    def clips(self):
        # type: () -> List[MidiClip]
        return super(SimpleMidiTrack, self).clips  # type: ignore

    def stop_midi_input_until_play(self):
        # type: () -> Sequence
        """ Just before the very end of the midi clip we temporarily disable midi input and stop the midi clip """
        seq = Sequence()
        input_routing_type = self.input_routing_type
        seq.add(partial(setattr, self, "input_routing_type", InputRoutingTypeEnum.NO_INPUT))
        seq.add(self.stop)
        seq.add(complete_on=self.song.selected_scene.is_triggered_listener, no_timeout=True)
        seq.add(partial(setattr, self, "input_routing_type", input_routing_type))
        return seq.done()
