import collections
from functools import partial

from _Framework.SubjectSlot import SlotManager
from typing import Optional, Dict, cast

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.FireSceneToPositionCommand import FireSceneToPositionCommand
from protocol0.domain.lom.scene.PlayingSceneFacade import PlayingSceneFacade
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.SceneFiredEvent import SceneFiredEvent
from protocol0.domain.lom.scene.ScenePositionScrolledEvent import ScenePositionScrolledEvent
from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.scheduler.ThirdBeatPassedEvent import ThirdBeatPassedEvent
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class ScenePlaybackService(SlotManager):
    _DEBUG = False

    def __init__(self, playback_component):
        # type: (PlaybackComponent) -> None
        super(ScenePlaybackService, self).__init__()
        self._playback_component = playback_component

        self._live_scene_id_to_scene = collections.OrderedDict()  # type: Dict[int, Scene]

        DomainEventBus.subscribe(BarChangedEvent, self._on_bar_changed_event)
        DomainEventBus.subscribe(ThirdBeatPassedEvent, self._on_third_beat_passed_event)
        DomainEventBus.subscribe(ScenePositionScrolledEvent, self._on_scene_position_scrolled_event)
        DomainEventBus.subscribe(SongStartedEvent, self._on_song_started_event)
        DomainEventBus.subscribe(SongStoppedEvent, self._on_song_stopped_event)
        DomainEventBus.subscribe(SceneFiredEvent, self._on_scene_fired_event)

    def _on_bar_changed_event(self, _):
        # type: (BarChangedEvent) -> None
        if SongFacade.playing_scene():
            SongFacade.playing_scene().scene_name.update()

    def _on_third_beat_passed_event(self, _):
        # type: (ThirdBeatPassedEvent) -> None
        if SongFacade.playing_scene() and SongFacade.playing_scene().playing_state.is_playing:
            SongFacade.playing_scene().on_end()

    def _on_scene_position_scrolled_event(self, _):
        # type: (ScenePositionScrolledEvent) -> None
        scene = SongFacade.selected_scene()
        Scene.LAST_MANUALLY_STARTED_SCENE = scene
        scene.scene_name.update(bar_position=scene.position_scroller.current_value)

    def fire_scene(self, scene):
        # type: (Scene) -> Optional[Sequence]
        # stop to start the scene right again
        # also it will stop the tails
        self._playback_component.stop()
        # not defer to avoid playback play / stop loops
        Scheduler.wait(5, scene.fire)
        return None

    def fire_scene_to_position(self, scene, bar_length=None):
        # type: (Scene, Optional[int]) -> None
        bar_length = self._get_position_bar_length(scene, bar_length)
        Scene.LAST_MANUALLY_STARTED_SCENE = scene
        self._playback_component.stop()

        if self._DEBUG:
            Logger.info("Firing %s to bar_length %s" % (scene, bar_length))

        if bar_length != 0:
            # removing click when changing position
            # (created by playing shortly the scene beginning)
            SongFacade.master_track().mute_for(250)

        # removes an artefact by changing too fast the playback state
        Scheduler.wait(1, partial(scene.fire_to_position, bar_length))

    def fire_previous_scene_to_last_bar(self):
        # type: () -> None
        previous_scene = SongFacade.selected_scene().previous_scene
        if previous_scene == SongFacade.selected_scene():
            self.fire_scene(previous_scene)
            return None

        self.fire_scene_to_position(previous_scene, previous_scene.bar_length - 1)

    def _get_position_bar_length(self, scene, bar_length):
        # type: (Scene, Optional[int]) -> int
        # as we use single digits
        if bar_length == 8:
            return scene.bar_length - 1
        if bar_length is None:
            return scene.position_scroller.current_value

        return bar_length

    def _on_song_started_event(self, _):
        # type: (SongStartedEvent) -> None
        # deferring because it can conflict with tail clips on fire scene to position
        if not ApplicationViewFacade.is_session_visible():
            return

        self._restart_inconsistent_scene()

    def _restart_inconsistent_scene(self):
        # type: () -> None
        """
        When the playback starts,
            - either manually (normal song play)
            - or from the script (command etc..)
        the scene can be in a inconsistent play state especially if an audio tail clip was
        previously playing but got muted

        We ignore playback from the script (handled) else
        we relaunch the scene cleanly
        """
        if not SongFacade.is_playing() or SongFacade.playing_scene() is None:
            return

        # do not trigger on already handled playback
        # playback can be inconsistent in some setups but we are handling it
        if CommandBus.has_recent_command(FireSceneToPositionCommand, 100):
            return

        # some clips are playing (scene is playing) but not all
        should_restart = any(
            not clip.is_playing and not clip.muted for clip in SongFacade.playing_scene().clips.all
        ) and any(clip.is_playing for clip in SongFacade.playing_scene().clips.all)
        if should_restart:
            self.fire_scene(cast(Scene, SongFacade.playing_scene()))

    def _on_song_stopped_event(self, _):
        # type: (SongStoppedEvent) -> None
        # don't activate when doing quick play / stop (e.g. in FireSelectedSceneCommand)
        if not SongFacade.is_playing():
            self._stop_previous_playing_scene()

        Scheduler.defer(self._mute_audio_tails)

    def _mute_audio_tails(self):
        # type: () -> None
        """On song stop : iterating all scenes because we don't know which tail might be playing"""
        for scene in SongFacade.scenes():
            for clip in scene.clips.audio_tail_clips:
                clip.muted = True

    def _on_scene_fired_event(self, event):
        # type: (SceneFiredEvent) -> None
        """Event is fired *before* the scene starts playing"""
        # Stop the previous scene : quantized or immediate
        playing_scene = SongFacade.playing_scene()
        fired_scene = SongFacade.scenes()[event.scene_index]

        if playing_scene is not None and playing_scene.index != event.scene_index:
            playing_scene.stop(immediate=not SongFacade.is_playing(), next_scene=fired_scene)

        # update the playing scene singleton at the next bar
        seq = Sequence()
        if SongFacade.is_playing():
            seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)
        seq.add(partial(PlayingSceneFacade.set, fired_scene))
        seq.done()

    def _stop_previous_playing_scene(self):
        # type: () -> None
        """
        Stop previous playing scene else on play
        tracks with tail from the previous scene are going to play again
        """
        if PlayingSceneFacade.get() is not None:
            for track in PlayingSceneFacade.get().abstract_tracks:
                if isinstance(track, AbstractGroupTrack):
                    track.dummy_group.reset_automation(
                        PlayingSceneFacade.get().index, immediate=True
                    )
        if PlayingSceneFacade.get_previous() is not None:
            PlayingSceneFacade.get_previous().stop(immediate=True)
