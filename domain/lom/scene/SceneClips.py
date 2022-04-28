from _Framework.SubjectSlot import subject_slot_group, SlotManager
from typing import List, cast, Iterator

from protocol0.domain.lom.clip.AudioTailClip import AudioTailClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.shared.decorators import throttle
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.observer.Observable import Observable


class SceneClips(SlotManager, Observable):
    def __init__(self, index):
        # type: (int) -> None
        super(SceneClips, self).__init__()
        self.index = index
        self.clip_slots = []  # type: List[ClipSlot]
        self._clips = []  # type: List[Clip]
        self.build()

    def __iter__(self):
        # type: () -> Iterator[Clip]
        return iter(self._clips)

    @subject_slot_group("has_clip")
    def _clip_slots_has_clip_listener(self, _):
        # type: (ClipSlot) -> None
        self._map_clips()
        self.notify_observers()

    @subject_slot_group("length")
    @throttle(wait_time=10)
    def _clips_length_listener(self, _):
        # type: (Clip) -> None
        self.notify_observers()

    @subject_slot_group("muted")
    def _clips_muted_listener(self, _):
        # type: (Clip) -> None
        self._map_clips()
        self.notify_observers()

    def build(self):
        # type: () -> None
        self.clip_slots = [track.clip_slots[self.index] for track in SongFacade.simple_tracks()]
        self._clip_slots_has_clip_listener.replace_subjects(self.clip_slots)

        self._map_clips()

    def _map_clips(self):
        # type: () -> None
        clips = [clip_slot.clip for clip_slot in self.clip_slots if
                 clip_slot.has_clip and clip_slot.clip and clip_slot.track.__class__ != SimpleInstrumentBusTrack]

        self._clips = [clip for clip in clips if not isinstance(clip, AudioTailClip)]
        self.audio_tail_clips = cast(List[AudioTailClip],
                                     [clip for clip in clips if isinstance(clip, AudioTailClip)])
        self._clips_length_listener.replace_subjects(self._clips)
        self._clips_muted_listener.replace_subjects([clip._clip for clip in self._clips])

    def on_added_scene(self):
        # type: () -> None
        """ Rename clips when doing consolidate time to new scene """
        if any(clip for clip in self._all_clips if clip.has_default_recording_name):
            for clip in self._all_clips:
                if isinstance(clip, AudioTailClip):
                    clip.delete()
                    continue

                if clip.has_default_recording_name:
                    clip.color = ClipColorEnum.AUDIO_UN_QUANTIZED.color_int_value
                clip.clip_name.update("")

    @property
    def _all_clips(self):
        # type: () -> List[Clip]
        return self._clips + self.audio_tail_clips
