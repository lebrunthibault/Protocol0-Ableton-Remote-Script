from functools import partial
from typing import TYPE_CHECKING, List

import Live

from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack


class AutomationMidiClipSlot(ClipSlot):
    """ special automation handling : the dummy audio clip is created on midi clip creation """
    def __init__(self, *a, **k):
        super(AutomationMidiClipSlot, self).__init__(*a, **k)
        self.clip = self.clip  # type: AutomationMidiClip
        self.track = self.track  # type: AutomationMidiTrack

    # @p0_subject_slot("has_clip")
    # def _has_clip_listener(self):
    #     super(AutomationMidiClipSlot, self)._has_clip_listener()
    #
    #     if self.clip and len(self.clip.get_notes()) == 0:
    #         self.configure_base_clip()
    #
    #     if self.clip and self.linked_clip_slot and not self.linked_clip_slot.clip:
    #         self.parent.defer(partial(self.linked_clip_slot.insert_dummy_clip, name=self.clip.name))

    def configure_base_clip(self):
        if not self.clip:
            return
        self.clip.view.grid_quantization = Live.Clip.GridQuantization.g_eighth
        self.clip.name = "%s (*,*)" % self.track.linked_track.automated_parameter.full_name
        velocities = [self.track.linked_track.automated_parameter.get_midi_value_from_value()]
        muted_start_note_velocities = [
            self.track.linked_track.automated_parameter.get_midi_value_from_value(self.track.linked_track.automated_parameter.min),
            self.track.linked_track.automated_parameter.get_midi_value_from_value(self.track.linked_track.automated_parameter.max)
        ]

        seq = Sequence()
        seq.add(partial(self.clip.replace_all_notes, self._get_equal_duration_notes(velocities=velocities,
                                                                   muted_start_note_velocities=muted_start_note_velocities)))
        seq.add(self.clip.view.hide_envelope)
        seq.add(wait=2)
        seq.add(self.parent.keyboardShortcutManager.click_clip_fold)
        seq.done()

    def _get_equal_duration_notes(self, velocities, muted_start_note_velocities):
        # type: (List[int], List[int]) -> List[Note]
        duration = self.clip.length / len(velocities)
        muted_start_note_velocities = [velo for velo in muted_start_note_velocities if velo not in velocities]
        muted_start_notes = [Note(pitch=vel, velocity=vel, start=0, duration=min(1, self.clip.length), muted=True, clip=self.clip)
                             for vel in
                             muted_start_note_velocities]
        self.clip._muted_notes = muted_start_notes
        return muted_start_notes + [Note(pitch=vel, velocity=vel, start=i * duration, duration=duration, clip=self.clip) for
                                    i, vel in
                                    enumerate(velocities)]