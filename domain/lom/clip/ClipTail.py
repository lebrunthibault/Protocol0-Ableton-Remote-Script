from functools import partial

from protocol0.domain.lom.scene.PlayingSceneFacade import PlayingSceneFacade
from protocol0.domain.lom.track.simple_track.SimpleTrackClipSlots import SimpleTrackClipSlots
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.shared.sequence.Sequence import Sequence


class ClipTail(object):
    def __init__(self, track_clip_slots):
        # type: (SimpleTrackClipSlots) -> None
        self.active = True
        self._track_clip_slots = track_clip_slots
        DomainEventBus.subscribe(BarChangedEvent, self._on_third_beat_passed_event)

    def _on_third_beat_passed_event(self, _):
        # type: (BarChangedEvent) -> None
        """
        Handling clip tail for end clips having length < scene length
        """
        if not self.active:
            return

        clip = self._track_clip_slots.playing_clip

        if clip is None:
            return

        playing_scene = PlayingSceneFacade.get()

        if playing_scene is None:
            return

        clip_slots = list(self._track_clip_slots)
        scene_index = playing_scene.index

        # activate tail only if the next clip slot is empty
        try:
            has_empty_next_cs = (
                clip_slots[scene_index + 1].clip is None
                or clip_slots[scene_index + 1].clip.muted
            )
        except IndexError:
            return

        # let the tail play
        if (
            has_empty_next_cs
            and playing_scene.playing_state.in_last_bar
            and not playing_scene.should_loop
            and clip.looping
            and clip.has_tail
        ):
            clip.looping = False
            seq = Sequence()
            seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)
            seq.wait_beats(clip.playing_position.beats_left + 1, continue_on_song_stop=True)
            seq.add(partial(setattr, clip, "looping", True))
            seq.done()
