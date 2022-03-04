from _Framework.CompoundElement import subject_slot_group
from typing import Optional, TYPE_CHECKING

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.clip.ClipSynchronizer import ClipSynchronizer
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot

if TYPE_CHECKING:
    from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot


class ClipSlotSynchronizer(UseFrameworkEvents):
    """ For ExternalSynthTrack """

    def __init__(self, midi_cs, audio_cs):
        # type: (MidiClipSlot, AudioClipSlot) -> None
        super(ClipSlotSynchronizer, self).__init__()
        self.midi_cs = midi_cs
        self.audio_cs = audio_cs

        self._has_clip_listener.replace_subjects([midi_cs, audio_cs])
        self._clip_synchronizer = None  # type: Optional[ClipSynchronizer]
        self._init_clip_synchronizer()

    def _init_clip_synchronizer(self):
        # type: () -> None
        if self._clip_synchronizer:
            self._clip_synchronizer.disconnect()

        if self.midi_cs.clip and self.audio_cs.clip:
            self._clip_synchronizer = ClipSynchronizer(midi_clip=self.midi_cs.clip, audio_clip=self.audio_cs.clip)
        else:
            self._clip_synchronizer = None

    @subject_slot_group("has_clip")
    def _has_clip_listener(self, _):
        # type: (ClipSlot) -> None
        self._init_clip_synchronizer()

    def disconnect(self):
        # type: () -> None
        super(ClipSlotSynchronizer, self).disconnect()
        if self._clip_synchronizer:
            self._clip_synchronizer.disconnect()
            self._clip_synchronizer = None
