from typing import Any, TYPE_CHECKING, Optional

from protocol0.application.faderfox.InterfaceState import InterfaceState
from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.shared.SongFacade import SongFacade

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
    from protocol0.domain.lom.clip_slot.AudioTailClipSlot import AudioTailClipSlot


class AudioTailClip(AudioClip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioTailClip, self).__init__(*a, **k)
        self.track = self.track  # type: SimpleAudioTailTrack
        self.clip_slot = self.clip_slot  # type: AudioTailClipSlot

    @property
    def midi_clip(self):
        # type: () -> Optional[MidiClip]
        return self.track.abstract_group_track.midi_track.clip_slots[self.index].clip

    @property
    def loop_end(self):
        # type: () -> float
        return super(AudioTailClip, self).loop_end

    # noinspection PyPropertyAccess
    @loop_end.setter
    def loop_end(self, loop_end):
        # type: (float) -> None
        """ make clip synchronizer work with the clip tail """
        self.loop_start = loop_end

    def post_record(self):
        # type: () -> None
        super(AudioTailClip, self).post_record()
        bar_length = InterfaceState.SELECTED_RECORDING_BAR_LENGTH.int_value
        if bar_length == 0:
            return None
        self.clip_name.update(base_name="")
        clip_end = bar_length * SongFacade.signature_numerator()

        self.looping = False
        self.loop_start = clip_end
        self.muted = True

    def play_and_mute(self):
        # type: () -> Sequence
        self.muted = False
        seq = Sequence()
        seq.add(wait=1)  # wait for unmute
        seq.add(self.fire)
        seq.add(wait_beats=1)
        seq.add(complete_on=self._playing_status_listener)
        seq.add(wait=10)
        seq.add(self._mute_if_stopped)
        return seq.done()

    def _mute_if_stopped(self):
        # type: () -> None
        if not self.is_playing:
            self.muted = True
