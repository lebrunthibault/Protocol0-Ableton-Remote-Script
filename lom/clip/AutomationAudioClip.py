from functools import partial

from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
    from a_protocol_0.lom.clip_slot.AutomationAudioClipSlot import AutomationAudioClipSlot
    from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip


class AutomationAudioClip(AbstractAutomationClip):
    def __init__(self, *a, **k):
        super(AutomationAudioClip, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationAudioTrack
        self.clip_slot = self.clip_slot  # type: AutomationAudioClipSlot
        self.automated_midi_clip = None  # type: AutomationMidiClip

        if self.track.automated_midi_track and not self.track.automated_midi_track.clip_slots[self.index].has_clip:
            self.delete()
            self.parent.show_message("Duplicating automation audio clips is not allowed")

    @property
    def linked_clip(self):
        # type: () -> AbstractAutomationClip
        return self.automated_midi_clip

    def _connect(self, midi_clip):
        # type: (AutomationMidiClip) -> None
        self.automated_midi_clip = midi_clip
        self._notes_listener.subject = midi_clip
        self._playing_status_listener.subject = midi_clip._clip
        seq = Sequence()
        seq.add(wait=1)
        seq.add(self._notes_listener)
        return seq.done()

    @subject_slot("notes")
    def _notes_listener(self):
        seq = Sequence()
        seq.add(self.clear_all_envelopes)
        seq.add(self._create_automation_envelope)
        return seq.done()

    def _create_automation_envelope(self):
        envelope = self.create_automation_envelope(self.track.automated_parameter)
        self.view.show_envelope()
        self.view.select_envelope_parameter(self.track.automated_parameter._device_parameter)
        self.view.show_loop()

        for note in self.automated_midi_clip._prev_notes:
            envelope.insert_step(note.start, note.duration, note.velocity)
