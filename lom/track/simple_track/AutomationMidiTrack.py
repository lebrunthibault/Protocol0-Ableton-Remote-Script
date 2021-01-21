from collections import OrderedDict
from functools import partial

from typing import List

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.clip.AutomationMidiClip import AutomationMidiClip
from a_protocol_0.lom.clip_slot.AutomationMidiClipSlot import AutomationMidiClipSlot
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence


class AutomationMidiTrack(SimpleTrack):
    def __init__(self, *a, **k):
        # type: (DeviceParameter) -> None
        super(AutomationMidiTrack, self).__init__(*a, **k)
        # this works here because the tracks are built left to right
        self.clip_slots = self.clip_slots  # type: List[AutomationMidiClipSlot]
        self.automated_audio_track = None  # type: AutomationAudioTrack
        self.ramping_steps = 13
        self.ramping_duration = 0.25  # eighth note
        self.push2_selected_main_mode = 'clip'
        self.push2_selected_matrix_mode = 'note'
        self.push2_selected_instrument_mode = 'split_melodic_sequencer'
        self.editing_clip = None  # type: AutomationMidiClip

    def _connect(self, track):
        # type: (AutomationAudioTrack) -> None
        self.automated_audio_track = track

    def _added_track_init(self):
        """ this can be called once, when the Live track is created """
        if self.group_track is None:
            raise Protocol0Error("An automation track should always be grouped")
        seq = Sequence()
        seq.add(wait=1)
        seq.add(lambda: [self.delete_device(d) for d in self.devices])

        if len(self.clips) == 0:
            seq.add(self._create_base_clips)
        return seq.done()

    def _create_base_clips(self):
        velocity_patterns = OrderedDict()
        velocity_patterns["dry"] = [127]
        # velocity_patterns["half-silent"] = [0, 127]
        # velocity_patterns["half-full"] = [127, 0]
        # velocity_patterns["quarter-silent"] = [0, 127, 127, 127]

        seq = Sequence()
        clip_creation_steps = []
        for i, (clip_name, velocities) in enumerate(velocity_patterns.items()):
            clip_creation_steps.append(partial(self.create_clip, slot_number=i, name=clip_name, bar_count=1,
                                               notes_callback=partial(self._fill_equal_notes, velocities=velocities)))

        seq.add(clip_creation_steps)
        seq.add(self.play)

        return seq.done()

    def _fill_equal_notes(self, clip, velocities):
        duration = clip.length / len(velocities)
        return [Note(pitch=vel, velocity=vel, start=i * duration, duration=duration, clip=clip) for i, vel in
                enumerate(velocities)]
