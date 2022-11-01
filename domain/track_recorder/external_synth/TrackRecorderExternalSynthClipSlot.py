from typing import Optional, Tuple

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.ClipSampleService import ClipToReplace
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.external_synth.ClipToReplaceDetectedEvent import (
    ClipToReplaceDetectedEvent,
)
from protocol0.shared.SongFacade import SongFacade


class SourceClipSlot(object):
    def __init__(self, track, scene_index, name):
        # type: (Optional[SimpleAudioTrack], int, str) -> None
        self.clip_slot = None  # type: Optional[AudioClipSlot]
        self._clip = None  # type: Optional[AudioClip]
        self._name = name

        if track is None or len(track.clip_slots) <= scene_index:
            return

        self.clip_slot = track.clip_slots[scene_index]
        self._clip = self.clip_slot.clip
        self.file_path = None  # type: Optional[str]
        if self._clip is not None:
            self.file_path = self._clip.file_path

        self.clip_slot.delete_clip()

    def post_record(self):
        # type: () -> None
        clip = self.clip_slot.clip
        # in case of manual stop
        if clip is None:
            return

        clip.muted = False
        clip.name = self._name

    def replace_clips(self):
        # type: () -> Tuple[int, int]
        clips_replaced_count = 0
        clips_count = 0

        tracks = SongFacade.simple_tracks(SimpleAudioTrack)
        clip_slots = [(t, cs) for t in tracks for cs in t.clip_slots if cs.clip]

        for track, clip_slot in clip_slots:
            clip = clip_slot.clip

            if clip.file_path != self.file_path:
                continue

            # dissociate between loop and end on clip length
            if self._name != "atk" and clip.length != self.clip_slot.clip.length:
                continue

            automated_params = clip.automation.get_automated_parameters(
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
