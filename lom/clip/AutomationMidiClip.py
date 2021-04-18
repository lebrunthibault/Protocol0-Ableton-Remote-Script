import Live
from typing import TYPE_CHECKING, List, Optional

from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.lom.clip.AutomationMidiClipNoteMixin import AutomationMidiClipNoteMixin
from a_protocol_0.lom.clip.MidiClip import MidiClip
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import debounce, p0_subject_slot

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
    from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
    from a_protocol_0.lom.clip.AutomationAudioClip import AutomationAudioClip


class AutomationMidiClip(AbstractAutomationClip, MidiClip, AutomationMidiClipNoteMixin):
    def __init__(self, *a, **k):
        super(AutomationMidiClip, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationMidiTrack
        self.clip_slot = None  # type: Optional[AutomationMidiClipSlot]
        self.linked_clip = None  # type: Optional[AutomationAudioClip]
        self._name_listener.subject = self._clip
        self._loop_start_listener.subject = self._clip
        self._loop_end_listener.subject = self._clip
        self._notes_listener.subject = self._clip

    def _on_selected(self):
        self.view.hide_envelope()
        self.view.show_loop()

    @p0_subject_slot("loop_start")
    def _loop_start_listener(self):
        self._refresh_notes()

    @p0_subject_slot("loop_end")
    def _loop_end_listener(self):
        self._refresh_notes()

    @p0_subject_slot("notes")
    def _notes_listener(self):
        # type: () -> Sequence
        if not self._is_updating_notes:
            return self.map_notes()

    @p0_subject_slot("name")
    def _name_listener(self):
        if self.name == self.clip_name.prev_name:
            return
        if len(self._prev_notes) >= 2:
            self._map_notes()

    def configure_new_clip(self):
        self.view.grid_quantization = Live.Clip.GridQuantization.g_eighth
        seq = Sequence()
        seq.add(super(AutomationMidiClip, self).configure_new_clip)
        if self.song.is_playing:
            seq.add(self.play)
        return seq.done()

    def generate_base_notes(self):
        # type: () -> List[Note]
        base_velocity = self.track.linked_track.automated_parameter.get_midi_value_from_value()
        base_note = Note(pitch=base_velocity, velocity=base_velocity, start=0, duration=self.length, clip=self)
        muted_start_note_velocities = [
            self.track.linked_track.automated_parameter.get_midi_value_from_value(velo)
            for velo in [
                self.track.linked_track.automated_parameter.min,
                self.track.linked_track.automated_parameter.max,
            ]
            if velo != base_velocity
        ]

        self._muted_notes = [
            Note(pitch=vel, velocity=vel, start=0, duration=min(1, int(self.length)), muted=True, clip=self)
            for vel in muted_start_note_velocities
        ]
        return self._muted_notes + [base_note]

    def _refresh_notes(self):
        self._prev_notes = self.get_notes()
        # noinspection PyUnresolvedReferences
        self.parent.defer(self.notify_notes)

    @debounce(17)
    def map_notes(self):
        notes = self.get_notes()
        if len(notes) == 0 or self._is_updating_notes or notes == self._prev_notes:
            return

        self._map_notes(notes)
