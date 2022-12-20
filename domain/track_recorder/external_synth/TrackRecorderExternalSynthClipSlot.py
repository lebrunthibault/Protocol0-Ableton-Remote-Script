from typing import Optional, Tuple

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.ClipSampleService import ClipToReplace
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.external_synth.ClipToReplaceDetectedEvent import (
    ClipToReplaceDetectedEvent,
)
from protocol0.shared.SongFacade import SongFacade


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

    def replace_clips(self):
        # type: () -> Tuple[int, int]
        if self.clip_slot is None or self.clip_slot.clip is None:
            return 0, 0

        clips_replaced_count = 0
        clips_count = 0

        tracks = (t for t in SongFacade.simple_tracks(SimpleAudioTrack) if t != self._track)
        clip_slots = [(t, cs) for t in tracks for cs in t.clip_slots if self.matches_cs(cs)]

        for track, clip_slot in clip_slots:
            if not self.matches_cs(clip_slot):
                continue

            automated_params = clip_slot.clip.automation.get_automated_parameters(
                track.devices.parameters
            )

            clips_count += 1

            # duplicate when no automation else manual action is needed
            if len(automated_params) == 0:
                clips_replaced_count += 1
                clip_slot.replace_clip(self.clip_slot)
            else:
                clip_to_replace = ClipToReplace(track, clip_slot, self.clip_slot.clip.file_path)
                DomainEventBus.emit(ClipToReplaceDetectedEvent(clip_to_replace))

        return clips_replaced_count, clips_count
