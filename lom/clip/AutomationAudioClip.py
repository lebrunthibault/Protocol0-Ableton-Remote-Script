from typing import TYPE_CHECKING

from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.utils.decorators import p0_subject_slot, retry

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
    from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip


class AutomationAudioClip(AbstractAutomationClip):
    def __init__(self, *a, **k):
        super(AutomationAudioClip, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationAudioTrack
        self.register_slot(self, self._post_init, "linked")  # on track instantiation
        self.linked_clip = self.linked_clip  # type: AutomationMidiClip

    def _post_init(self):
        self._notes_listener.subject = self.linked_clip
        self.parent.defer(self._notes_listener)  # deferring change

    def _on_selected(self):
        self.view.show_envelope()
        self.view.select_envelope_parameter(self.track.automated_parameter._device_parameter)
        self.view.show_loop()

    @p0_subject_slot("notes")
    def _notes_listener(self):
        """ retry is on clip creation : the clip is created but the device can take longer to load """
        if not self._clip:
            return

        self.clear_all_envelopes()
        envelope = self.create_automation_envelope(self.track.automated_parameter)

        if self.linked_clip:
            for note in self.linked_clip.automation_notes:
                envelope.insert_step(note.start, note.duration,
                                     self.track.automated_parameter.get_value_from_midi_value(note.velocity))

    def _insert_step(self, start, duration, velocity):
        range = self.track.automated_parameter.max - self.track.automated_parameter.min
