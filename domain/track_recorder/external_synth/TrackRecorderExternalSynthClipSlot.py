from functools import partial

from typing import Optional, cast, List

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.sequence.Sequence import Sequence


class SourceClipSlot(object):
    def __init__(self, track, scene_index, name):
        # type: (Optional[SimpleAudioTrack], int, str) -> None
        self.clip_slot = None  # type: Optional[AudioClipSlot]
        self._name = name
        self._track = track

        if track is None or len(track.clip_slots) <= scene_index:
            return

        self.clip_slot = track.clip_slots[scene_index]
        assert self.clip_slot, "Cannot find clip_slot on %s at index %s" % (track, scene_index)
        self.file_path = None  # type: Optional[str]
        if self.clip is not None:
            self.file_path = self.clip.file_path

        self.clip_slot.delete_clip()

    def __repr__(self):
        # type: () -> str
        return "%s - %s" % (self._track, self._name)

    @property
    def clip(self):
        # type: () -> Optional[AudioClip]
        if self.clip_slot is None:
            return None
        else:
            return self.clip_slot.clip

    def matches_cs(self, clip_slot):
        # type: (AudioClipSlot) -> bool
        if clip_slot.clip is None or self.clip is None:
            return False

        if not liveobj_valid(clip_slot.clip._clip):
            return False

        if clip_slot == self.clip_slot:
            return False

        return clip_slot.clip.file_path == self.file_path

    def post_record(self):
        # type: () -> None
        clip = self.clip_slot.clip if self.clip_slot is not None else None
        # in case of manual stop
        if clip is None:
            return

        clip.looping = True
        clip.muted = False
        clip.name = self._name

    @property
    def matching_clip_slots(self):
        # type: () -> List[AudioClipSlot]
        matching_track = cast(ExternalSynthTrack, self._track.abstract_track).matching_track._track
        if matching_track is None:
            return []
        else:
            return [cs for cs in matching_track.clip_slots if self.matches_cs(cs)]

    def replace_clips(self):
        # type: () -> Sequence
        matching_track = cast(ExternalSynthTrack, self._track.abstract_track).matching_track._track

        seq = Sequence()
        for clip_slot in self.matching_clip_slots:
            device_params = matching_track.devices.parameters
            automated_params = clip_slot.clip.automation.get_automated_parameters(device_params)

            # duplicate when no automation else manual action is needed
            if len(automated_params) == 0:
                clip_slot.replace_clip_sample(self.clip_slot)
            else:
                seq.add(partial(clip_slot.replace_clip_sample, None, self.clip_slot.clip.file_path))

        seq.add(partial(Backend.client().close_explorer_window, "Recorded"))

        return seq.done()
