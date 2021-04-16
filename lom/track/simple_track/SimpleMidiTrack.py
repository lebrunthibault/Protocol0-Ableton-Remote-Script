from a_protocol_0.lom.clip.MidiClip import MidiClip
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleMidiTrack(SimpleTrack):
    CLIP_CLASS = MidiClip

    def __init__(self, *a, **k):
        super(SimpleMidiTrack, self).__init__(*a, **k)
        self.push2_selected_matrix_mode = "note"
        self.push2_selected_instrument_mode = "split_melodic_sequencer"
