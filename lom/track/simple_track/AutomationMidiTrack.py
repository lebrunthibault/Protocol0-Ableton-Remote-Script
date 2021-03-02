from collections import OrderedDict
from functools import partial

from typing import List, TYPE_CHECKING

from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.AbstractAutomationTrack import AbstractAutomationTrack
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack


class AutomationMidiTrack(AbstractAutomationTrack):
    def __init__(self, *a, **k):
        # type: (DeviceParameter) -> None
        super(AutomationMidiTrack, self).__init__(*a, **k)
        # this works here because the tracks are built left to right
        self.linked_track = None  # type: AutomationAudioTrack

        self.clip_slots = self.clip_slots  # type: List[AutomationMidiClipSlot]
        self.push2_selected_main_mode = 'clip'
        self.push2_selected_matrix_mode = 'note'
        self.push2_selected_instrument_mode = 'split_melodic_sequencer'

    def _added_track_init(self):
        """ when this is called the AutomatedTrack and AutomationAudioTrack are fully loaded """
        self.clear_devices()
        velocity_patterns = OrderedDict()
        clip_name = "%s (*,*)" % self.linked_track.automated_parameter.full_name
        clip_velocities = [self.linked_track.automated_parameter.get_midi_value_from_value()]
        muted_start_note_velocities = [
            self.linked_track.automated_parameter.get_midi_value_from_value(self.linked_track.automated_parameter.min),
            self.linked_track.automated_parameter.get_midi_value_from_value(self.linked_track.automated_parameter.max)
        ]

        seq = Sequence()
        seq.add(partial(self._create_base_clip, clip_slot_index=self.song.selected_scene_index, name=clip_name,
                        velocities=clip_velocities, muted_start_note_velocities=muted_start_note_velocities))
        seq.add(partial(self.track_name.set, playing_slot_index=self.song.selected_scene_index))
        seq.add(partial(self.linked_track.track_name.set, playing_slot_index=self.song.selected_scene_index))
        seq.add(self.linked_track.play)

        return seq.done()

    def _create_base_clip(self, clip_slot_index, name, velocities, muted_start_note_velocities):
        # type: (int, str, List[int], List[int]) -> Sequence
        seq = Sequence()
        seq.add(partial(self.create_clip, clip_slot_index=clip_slot_index, name=name, bar_count=1))
        seq.add(
            partial(lambda cs: cs.clip.replace_all_notes(self._get_equal_duration_notes(velocities=velocities,
                                                                                        muted_start_note_velocities=muted_start_note_velocities,
                                                                                        clip=cs.clip)),
                    self.clip_slots[clip_slot_index]), name="set clip notes")
        seq.add(partial(lambda cs: cs.clip.view.hide_envelope(),
                        self.clip_slots[clip_slot_index]))
        return seq.done()

    def _get_equal_duration_notes(self, clip, velocities, muted_start_note_velocities):
        # type: (Clip, List[int], List[int]) -> List[Note]
        duration = clip.length / len(velocities)
        muted_start_note_velocities = [velo for velo in muted_start_note_velocities if velo not in velocities]
        muted_start_notes = [Note(pitch=vel, velocity=vel, start=0, duration=min(1, clip.length), muted=True, clip=clip) for vel in
                             muted_start_note_velocities]
        clip._muted_notes = muted_start_notes
        return muted_start_notes + [Note(pitch=vel, velocity=vel, start=i * duration, duration=duration, clip=clip) for
                                    i, vel in
                                    enumerate(velocities)]
