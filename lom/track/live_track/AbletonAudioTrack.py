from typing import List

import Live
from _Framework.SubjectSlot import Subject


class AbletonAudioTrack(Subject):
    __subject_events__ = ("solo", "name", "devices", "clip_slots", "playing_slot_index", "fired_slot_index", "color")

    def __init__(self):
        # type: () -> None
        self.name = "ableton track"
        self.devices = []  # type: List[Live.Device.Device]
        self.can_be_armed = True
        self.arm = False
        self.fold_state = False
        self.is_foldable = False
        self.is_visible = True
        self.clip_slots = []  # type: List[Live.ClipSlot.ClipSlot]
        self.view = None
        self.group_track = None
        self.color_index = 0
        self.has_audio_input = False
        self.has_audio_output = True
        self.has_midi_input = False
        self.has_audio_input = True
        self.solo = False
