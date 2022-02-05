from typing import Optional

import Live
from protocol0.application.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.infra.SongDataManager import SongDataManager
from protocol0.application.config import Config
from protocol0.domain.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.domain.enums.SongLoadStateEnum import SongLoadStateEnum
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.application.faderfox.InterfaceState import InterfaceState
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.infra.System import System


class SongManager(AbstractControlSurfaceComponent):
    def init_song(self):
        # type: () -> None
        self.parent.songTracksManager.tracks_listener()
        self.parent.songScenesManager.scenes_listener()
        self.song.song_load_state = SongLoadStateEnum.LOADING
        if Config.ABLETON_SESSION_TYPE == AbletonSessionTypeEnum.PROFILING:
            return None

        if self.song.clip_trigger_quantization == Live.Song.Quantization.q_no_q:
            System.get_instance().show_warning("The global launch quantization is set to None")

        for armed_track in self.song.armed_tracks:
            self.parent.defer(armed_track.unarm)

        startup_track = self._get_startup_track()
        self._restore_selected_state()
        if startup_track:
            seq = Sequence()
            seq.add(wait=2)
            seq.add(startup_track.select)
            seq.add(self.parent.sessionManager.toggle_session_ring)
            seq.done()
        self.parent.wait(2, self.song.reset)

    def _restore_selected_state(self):
        # type: () -> None
        if SongDataManager.SELECTED_SCENE_INDEX is not None and SongDataManager.SELECTED_SCENE_INDEX < len(
                self.song.scenes):
            selected_scene = self.song.scenes[SongDataManager.SELECTED_SCENE_INDEX]
            selected_scene.select()
        if SongDataManager.SELECTED_TRACK_INDEX is not None and SongDataManager.SELECTED_TRACK_INDEX < len(
                list(self.song.all_simple_tracks)):
            selected_track = list(self.song.all_simple_tracks)[SongDataManager.SELECTED_TRACK_INDEX]
            selected_track.select()
        if SongDataManager.LAST_MANUALLY_STARTED_SCENE_INDEX is not None and SongDataManager.LAST_MANUALLY_STARTED_SCENE_INDEX < len(
                list(self.song.scenes)):
            scene = self.song.scenes[SongDataManager.LAST_MANUALLY_STARTED_SCENE_INDEX]
            if not SongDataManager.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION or SongDataManager.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION < scene.bar_length:
                Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = SongDataManager.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION
            Scene.LAST_MANUALLY_STARTED_SCENE = scene

    def _get_startup_track(self):
        # type: () -> Optional[AbstractTrack]
        if InterfaceState.FOCUS_PROPHET_ON_STARTUP:
            first_prophet_track = next(self.song.prophet_tracks, None)
            if first_prophet_track:
                return first_prophet_track
            else:
                raise Protocol0Warning("Couldn't find prophet track")

        armed_tracks = self.song.armed_tracks
        if len(armed_tracks):
            return armed_tracks[0]

        if self.song.selected_track == self.song.master_track:
            return next(self.song.abstract_tracks)

        return None

    def scroll_tempo(self, go_next):
        # type: (bool) -> None
        increment = 1 if go_next else -1
        self.song.tempo += increment
