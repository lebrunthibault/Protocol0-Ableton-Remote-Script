from collections import OrderedDict
from functools import partial

from _Framework.Util import find_if
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.Note import Note
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence


class AutomationMidiTrack(SimpleTrack):
    def __init__(self, *a, **k):
        # type: (DeviceParameter) -> None
        super(AutomationMidiTrack, self).__init__(*a, **k)
        self.automated_track = self.song.next_track(-1)
        [_, device_name, parameter_name] = self.automated_track.name.split(":")
        self.automated_parameter = find_if(lambda p: p.name == parameter_name,
                                           find_if(lambda d: d.name == device_name,
                                                   self.automated_track.devices))  # type: DeviceParameter
        self.ramping_steps = 13
        self.ramping_duration = 0.25  # eighth note
        self.push2_selected_main_mode = 'clip'
        self.push2_selected_matrix_mode = 'note'
        self.push2_selected_instrument_mode = 'split_melodic_sequencer'
        self.editing_clip = None  # type: Clip

    def _added_track_init(self):
        """ this can be called once, when the Live track is created """
        if self.group_track is None:
            raise RuntimeError("An automation track should always be grouped")
        [self.delete_device(d) for d in self.devices]
        seq = Sequence()
        # self.output_routing_type = find_if(lambda r: r.attached_object == self.group_track._track,
        #                                    self.available_output_routing_types)
        # seq.add(wait=1)
        # seq.add(lambda: setattr(self, "output_routing_channel", find_last(lambda r: "lfotool" in r.display_name.lower(),
        #                                                                   self.available_output_routing_channels)))

        if len(self.clips) == 0:
            seq.add(self._create_base_clips)
        seq.done()()

    def _create_base_clips(self):
        velocity_patterns = OrderedDict()
        velocity_patterns["dry"] = [127]
        velocity_patterns["half-silent"] = [0, 127]
        velocity_patterns["half-full"] = [127, 0]
        velocity_patterns["quarter-silent"] = [0, 127, 127, 127]

        for i, (clip_name, velocities) in enumerate(velocity_patterns.items()):
            self.create_clip(slot_number=i, name=clip_name, bar_count=1,
                             notes_callback=partial(self._fill_equal_notes, velocities=velocities))

        Sequence().add(complete_on=self.clip_slots[0]._has_clip_listener).add(self.play).done()()

    def create_clip(self, slot_number=0, name=None, bar_count=1, notes_callback=None, sync=True):
        # type: (int, str, int, callable, int) -> None
        seq = super(AutomationMidiTrack, self).create_clip(slot_number, name, bar_count, notes_callback, sync)
        seq.add(lambda: self.automated_track.clip_slots[slot_number].insert_dummy_clip())

    def _fill_equal_notes(self, clip, velocities):
        duration = clip.length / len(velocities)
        return [Note(pitch=vel, velocity=vel, start=i * duration, duration=duration, clip=clip) for i, vel in
                enumerate(velocities)]
