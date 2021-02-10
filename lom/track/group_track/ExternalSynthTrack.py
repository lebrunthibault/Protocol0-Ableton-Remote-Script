from typing import TYPE_CHECKING
import Live

from _Framework.Util import forward_property
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.ExternalSynthTrackActionMixin import ExternalSynthTrackActionMixin
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import find_last

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class ExternalSynthTrack(ExternalSynthTrackActionMixin, AbstractGroupTrack):
    def __init__(self, group_track, *a, **k):
        # type: (SimpleTrack) -> None
        super(ExternalSynthTrack, self).__init__(group_track=group_track, *a, **k)
        self.midi = find_last(lambda t: t.is_midi, self.sub_tracks)  # type: SimpleTrack
        self.audio = find_last(lambda t: t.is_audio, self.sub_tracks)  # type: SimpleTrack
        self.instrument_track = self.midi
        self.midi.is_scrollable = self.audio.is_scrollable = False
        self._instrument_listener.subject = self.instrument_track
        self._instrument_listener()

    @property
    def arm(self):
        # type: () -> bool
        return self.midi.arm and self.audio.arm

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi.is_playing or self.audio.is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return self.midi.is_recording or self.audio.is_recording

    def _post_record(self):
        self.song.metronome = False
        self.midi.has_monitor_in = False
        seq = Sequence().add(wait=2)
        seq.add(lambda: setattr(self.audio.playable_clip, "warp_mode", Live.Clip.WarpMode.complex_pro))
        seq.add(lambda: self.audio.playable_clip.quantize())
        return seq.done()

    @property
    def next_empty_clip_slot_index(self):
        # type: () -> ClipSlot
        for i in range(len(self.song.scenes)):
            if not self.midi.clip_slots[i].has_clip and not self.audio.clip_slots[i].has_clip:
                return i
        self.song.create_scene()
        return len(self.song.scenes) - 1

    @forward_property('audio')
    def set_output_routing_type(self): pass
