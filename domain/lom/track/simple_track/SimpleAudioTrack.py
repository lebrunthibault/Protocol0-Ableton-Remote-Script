from functools import partial

from typing import List, cast, Optional, Any

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.scene.PlayingSceneFacade import PlayingSceneFacade
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.scheduler.ThirdBeatPassedEvent import ThirdBeatPassedEvent
from protocol0.shared.sequence.Sequence import Sequence


class SimpleAudioTrack(SimpleTrack):
    CLIP_SLOT_CLASS = AudioClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)
        DomainEventBus.subscribe(ThirdBeatPassedEvent, self._on_third_beat_passed_event)

    @property
    def clip_slots(self):
        # type: () -> List[AudioClipSlot]
        return cast(List[AudioClipSlot], super(SimpleAudioTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[AudioClip]
        return cast(List[AudioClip], super(SimpleAudioTrack, self).clips)

    @property
    def playing_clip(self):
        # type: () -> Optional[AudioClip]
        return super(SimpleAudioTrack, self).playing_clip

    def stop(self, scene_index=None, next_scene_index=None, immediate=False):
        # type: (Optional[int], Optional[int], bool) -> None
        """
        Will stop the track immediately or quantized
        the scene_index is useful for fine tuning the stop of abstract group tracks
        """
        if scene_index is None:
            return super(SimpleAudioTrack, self).stop(scene_index, next_scene_index, immediate)

        # let tail play
        clip = self.clip_slots[scene_index].clip
        if clip is not None and clip.is_playing:
            Scheduler.wait_bars(clip.playing_position.bars_left, clip.stop)

    def _on_third_beat_passed_event(self, _):
        # type: (ThirdBeatPassedEvent) -> None
        """
        Handling clip tail for end clips having length < scene length
        """
        clip = self.playing_clip

        if clip is None:
            return

        from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import \
            ExternalSynthTrack
        if isinstance(self.abstract_group_track, ExternalSynthTrack):
            return

        # let the tail play
        if PlayingSceneFacade.get().playing_state.in_last_bar and clip.looping and clip.has_tail:
            clip.looping = False
            seq = Sequence()
            seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)
            seq.wait_bars(clip.playing_position.bars_left, continue_on_song_stop=True)
            seq.add(partial(setattr, clip, "looping", True))
            seq.done()
