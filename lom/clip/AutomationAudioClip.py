from functools import partial

from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot_group
from a_protocol_0.automation.AutomationCurveGenerator import AutomationCurveGenerator
from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.lom.clip.AudioClip import AudioClip
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
    from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip


class AutomationAudioClip(AbstractAutomationClip, AudioClip):
    def __init__(self, *a, **k):
        super(AutomationAudioClip, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationAudioTrack
        self._linked_listener.subject = self
        self.linked_clip = None  # type: AutomationMidiClip
        self.parent.defer(partial(setattr, self, "warping", True))

    @p0_subject_slot("linked")
    def _linked_listener(self):
        """ linked clip is available """
        self._notes_listener.subject = self.linked_clip
        self.parent.defer(self._notes_listener)  # deferring change
        self._ramp_change_listener.replace_subjects(
            [
                self.automation_ramp_up,
                self.automation_ramp_down,
            ]
        )

    def _on_selected(self):
        self.view.show_envelope()
        self.view.select_envelope_parameter(self.track.automated_parameter._device_parameter)
        self.view.show_loop()

    @subject_slot_group("ramp_change")
    def _ramp_change_listener(self, ramp_mode):
        self._notes_listener()

    @p0_subject_slot("notes")
    def _notes_listener(self):
        """ retry is on clip creation : the clip is created but the device can take longer to load """
        if not self._clip:
            return

        envelope = self.automation_envelope(self.track.automated_parameter)

        if not envelope:
            self.clear_all_envelopes()
            envelope = self.create_automation_envelope(self.track.automated_parameter)

        if self.linked_clip:
            for note in AutomationCurveGenerator.automation_notes(self.linked_clip):
                envelope.insert_step(
                    note.start,
                    note.duration,
                    self.track.automated_parameter.get_value_from_midi_value(note.velocity),
                )
