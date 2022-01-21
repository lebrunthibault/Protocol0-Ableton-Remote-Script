from functools import partial

from protocol0.enums.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.track_recorder.decorator.external_synth.abstract_track_recorder_external_synth_decorator import \
    AbstractTrackRecorderExternalSynthDecorator
from protocol0.sequence.Sequence import Sequence


class TrackRecorderStopMidiInputDecorator(AbstractTrackRecorderExternalSynthDecorator):
    def record(self, bar_length):
        # type: (int) -> Sequence
        if self.track.record_clip_tails and bar_length != 0:
            midi_clip_slot = self.track.midi_track.clip_slots[self.recording_scene_index]
            self._stop_midi_input_until_play(midi_clip_slot=midi_clip_slot)
        return super(TrackRecorderStopMidiInputDecorator, self).record(bar_length)

    def _stop_midi_input_until_play(self, midi_clip_slot):
        # type: (MidiClipSlot) -> None
        """ Just before the very end of the midi clip we temporarily disable midi input and stop the midi clip """
        input_routing_type = self.track.midi_track.input_routing_type

        seq = Sequence()
        seq.add(complete_on=midi_clip_slot.recording_ended_listener)
        seq.add(partial(setattr, self, "input_routing_type", InputRoutingTypeEnum.NO_INPUT))
        seq.add(self.track.midi_track.stop)
        seq.add(complete_on=self.song.selected_scene.is_triggered_listener, no_timeout=True)
        seq.add(partial(setattr, self, "input_routing_type", input_routing_type))
        seq.done()
