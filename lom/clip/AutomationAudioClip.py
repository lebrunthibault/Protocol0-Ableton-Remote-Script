from functools import partial

from typing import TYPE_CHECKING

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.lom.clip.Clip import Clip
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

    def _connect(self, clip):
        # type: (AutomationMidiClip) -> None
        self.automated_midi_clip = clip
        self._sync_name.subject = self.automated_midi_clip
        self._notes_listener.subject = self.automated_midi_clip
        self._playing_status_listener.subject = self.automated_midi_clip._clip
        self.parent.log_debug("in audio _connect : self: %s, self.automated_midi_clip: %s" % (self, self.automated_midi_clip))
        seq = Sequence()
        seq.add(wait=1)
        seq.add(partial(setattr, self, "name", clip.name), name="set audio clip name")
        seq.add(partial(setattr, self, "end_marker", clip.length), name="set audio clip end_marker")
        seq.add(partial(setattr, self, "loop_end", clip.length), name="set audio clip loop_end")
        seq.add(self._notes_listener)
        return seq.done()

    @subject_slot("name")
    def _sync_name(self):
        self.name = self.automated_midi_clip.name

    @subject_slot("notes")
    def _notes_listener(self):
        seq = Sequence()
        seq.add(self.clear_all_envelopes)
        seq.add(self._create_automation_envelope)
        return seq.done()

    def _create_automation_envelope(self):
        envelope = self.create_automation_envelope(self.track.automated_parameter)
        for note in self.automated_midi_clip._prev_notes:
            envelope.insert_step(note.start, note.duration, note.velocity)
