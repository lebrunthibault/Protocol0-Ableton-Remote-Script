from collections import OrderedDict
from functools import partial

from typing import List, TYPE_CHECKING

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
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
        self.clip_slots = self.clip_slots  # type: List[AutomationMidiClipSlot]
        self.automated_audio_track = None  # type: AutomationAudioTrack
        self.push2_selected_main_mode = 'clip'
        self.push2_selected_matrix_mode = 'note'
        self.push2_selected_instrument_mode = 'split_melodic_sequencer'
        self.editing_clip = None  # type: AutomationMidiClip
        self.automated_audio_track = None  # type: AutomationAudioTrack

    def _connect(self, track):
        # type: (AutomationAudioTrack) -> None
        first_connection = self.automated_audio_track is None
        self.automated_audio_track = track
        self.automated_audio_track._connect(self)
        if first_connection and len(self.clips) == 0:
            self._create_base_clips()

    def _added_track_init(self):
        """ this can be called once, when the Live track is created """
        if self.group_track is None:
            raise Protocol0Error("An automation track should always be grouped")
        seq = Sequence()
        seq.add(wait=1)
        seq.add(lambda: [self.delete_device(d) for d in self.devices])
        return seq.done()

    def _create_base_clips(self):
        velocity_patterns = OrderedDict()
        name = self.automated_audio_track.automated_parameter.full_name
        velocity_patterns["%s (*,*)" % name] = [self.automated_audio_track.automated_parameter.get_midi_value_from_value()]

        seq = Sequence()
        clip_creation_steps = []
        for i, (clip_name, velocities) in enumerate(velocity_patterns.items()):
            seq.add(partial(self._create_base_clip, clip_slot_index=i, name=clip_name, velocities=velocities))
            # the following creates a bug with push when adding multiple clips
            # clip_creation_steps.append(partial(self._create_base_clip, clip_slot_index=i, name=clip_name, velocities=velocities))

        # seq.add(clip_creation_steps)
        seq.add(lambda: self.automated_audio_track.play())

        return seq.done()

    def _create_base_clip(self, clip_slot_index, name, velocities):
        seq = Sequence()
        seq.add(partial(self.create_clip, clip_slot_index=clip_slot_index, name=name, bar_count=1))
        seq.add(
            partial(lambda cs: cs.clip.replace_all_notes(self._fill_equal_notes(velocities=velocities, clip=cs.clip)),
                    self.clip_slots[clip_slot_index]), name="set clip notes")
        seq.add(partial(lambda cs: cs.clip._map_notes(),
                        self.clip_slots[clip_slot_index]), name="process notes")
        seq.add(partial(lambda cs: cs.clip.view.hide_envelope(),
                        self.clip_slots[clip_slot_index]))
        return seq.done()

    def _fill_equal_notes(self, clip, velocities):
        duration = clip.length / len(velocities)
        return [Note(pitch=vel, velocity=vel, start=i * duration, duration=duration, clip=clip) for i, vel in
                enumerate(velocities)]
