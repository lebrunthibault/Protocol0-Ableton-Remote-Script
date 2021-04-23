from functools import partial

from typing import TYPE_CHECKING, Optional, Any

from _Framework.SubjectSlot import subject_slot_group
from a_protocol_0.automation.AutomationCurveGenerator import AutomationCurveGenerator
from a_protocol_0.automation.AutomationRampMode import AutomationRampMode
from a_protocol_0.enums.DirectionEnum import DirectionEnum
from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.lom.clip.AudioClip import AudioClip
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
    from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip


class AutomationAudioClip(AbstractAutomationClip, AudioClip):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AutomationAudioClip, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationAudioTrack
        self._linked_listener.subject = self
        self.linked_clip = None  # type: Optional[AutomationMidiClip]
        self.parent.defer(partial(setattr, self, "warping", True))
        self.automation_ramp_up = AutomationRampMode(direction=DirectionEnum.UP)  # type: AutomationRampMode
        self.automation_ramp_down = AutomationRampMode(direction=DirectionEnum.DOWN)  # type: AutomationRampMode

    @p0_subject_slot("linked")
    def _linked_listener(self):
        # type: () -> None
        """ linked clip is available """
        self._notes_listener.subject = self.linked_clip
        self._ramp_change_listener.replace_subjects(
            [
                self.automation_ramp_up,
                self.automation_ramp_down,
            ]
        )

    def _on_selected(self):
        # type: () -> None
        self.displayed_automated_parameter(self.track.automated_parameter)

    @subject_slot_group("ramp_change")
    def _ramp_change_listener(self, ramp_mode):
        # type: (AutomationRampMode) -> None
        self._notes_listener()

    @p0_subject_slot("notes")
    def _notes_listener(self):
        # type: () -> None
        """ retry is on clip creation : the clip is created but the device can take longer to load """
        if not self._clip or not self.track.automated_parameter:
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
