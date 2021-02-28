from _Framework.SubjectSlot import subject_slot
from typing import TYPE_CHECKING

from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
    from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip


class AutomationAudioClip(AbstractAutomationClip):
    def __init__(self, *a, **k):
        super(AutomationAudioClip, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationAudioTrack
        self.parent.defer(self._linked_clip_init)

    @property
    def linked_clip(self):
        # type: () -> AutomationMidiClip
        return super(AutomationAudioClip, self).linked_clip

    def _linked_clip_init(self):
        self._notes_listener.subject = self.linked_clip
        self._notes_listener

    def _on_selected(self):
        self.view.show_envelope()
        self.view.select_envelope_parameter(self.track.automated_parameter._device_parameter)
        self.view.show_loop()

    @subject_slot("notes")
    def _notes_listener(self):
        if not self._clip:
            return
        seq = Sequence()
        seq.add(self.clear_all_envelopes)
        seq.add(self._create_automation_envelope)
        return seq.done()

    def _create_automation_envelope(self):
        if not self.track.automated_parameter:
            self.track._set_automated_device_and_parameter()
        envelope = self.create_automation_envelope(self.track.automated_parameter)

        if self.linked_clip:
            for note in self.linked_clip.automation_notes:
                envelope.insert_step(note.start, note.duration,
                                     self.track.automated_parameter.get_value_from_midi_value(note.velocity))

    def _insert_step(self, start, duration, velocity):
        range = self.track.automated_parameter.max - self.track.automated_parameter.min
