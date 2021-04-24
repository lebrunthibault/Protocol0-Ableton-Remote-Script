import Live
from typing import TYPE_CHECKING, Optional, Any

from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.lom.clip.AutomationMidiClipNoteMixin import AutomationMidiClipNoteMixin
from a_protocol_0.lom.clip.MidiClip import MidiClip
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import debounce, p0_subject_slot

if TYPE_CHECKING:
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
    from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot


class AutomationMidiClip(AbstractAutomationClip, MidiClip, AutomationMidiClipNoteMixin):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AutomationMidiClip, self).__init__(*a, **k)
        self.track = self.track  # type: AutomationMidiTrack
        self.clip_slot = self.clip_slot  # type: AutomationMidiClipSlot
        self._name_listener.subject = self._clip
        self._length_listener.subject = self
        self._notes_listener.subject = self._clip

    def _on_selected(self):
        # type: () -> None
        self.view.hide_envelope()
        self.view.show_loop()

    @p0_subject_slot("length")
    def _length_listener(self):
        # type: () -> None
        self._refresh_notes()

    @p0_subject_slot("notes")
    def _notes_listener(self):
        # type: () -> Optional[Sequence]
        if not self._is_updating_notes:
            return self.map_notes()
        return None

    @p0_subject_slot("name")
    def _name_listener(self):
        # type: () -> None
        if self.name == self.clip_name.prev_name:
            return
        if len(self._prev_notes) >= 2:
            self._map_notes()

    def configure_new_clip(self):
        # type: () -> Sequence
        self.view.grid_quantization = Live.Clip.GridQuantization.g_eighth
        seq = Sequence()
        seq.add(super(AutomationMidiClip, self).configure_new_clip)
        if self.song.is_playing:
            seq.add(self.play)
        return seq.done()

    def _refresh_notes(self):
        # type: () -> None
        self._prev_notes = self.get_notes()
        # noinspection PyUnresolvedReferences
        self.parent.defer(self.notify_notes)

    @debounce(17)
    def map_notes(self):
        # type: () -> None
        notes = self.get_notes()
        if len(notes) == 0 or self._is_updating_notes or notes == self._prev_notes:
            return

        self._map_notes(notes)
