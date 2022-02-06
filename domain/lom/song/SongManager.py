from typing import Optional

import Live
from protocol0.application.config import Config
from protocol0.application.interface.SessionManager import SessionManager
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.SongScenesManager import SongScenesManager
from protocol0.domain.lom.song.SongTracksManager import SongTracksManager
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.infra.SongDataManager import SongDataManager
from protocol0.infra.System import System
from protocol0.infra.scheduler.Scheduler import Scheduler
from protocol0.shared.AccessSong import AccessSong


class SongManager(AccessSong):
    def __init__(self, song_tracks_manager, song_scenes_manager, session_manager):
        # type: (SongTracksManager, SongScenesManager, SessionManager) -> None
        self._song_tracks_manager = song_tracks_manager
        self._song_scenes_manager = song_scenes_manager
        self._session_manager = session_manager

    def init_song(self):
        # type: () -> None
        self._song_tracks_manager.tracks_listener()
        self._song_scenes_manager.scenes_listener()

        if self._song.clip_trigger_quantization == Live.Song.Quantization.q_no_q:
            System.get_instance().show_warning("The global launch quantization is set to None")

        for armed_track in self._song.armed_tracks:
            Scheduler.defer(armed_track.unarm)

        startup_track = self._get_startup_track()
        self._restore_selected_state()
        if startup_track:
            seq = Sequence()
            seq.add(wait=2)
            seq.add(startup_track.select)
            seq.add(self._session_manager.toggle_session_ring)
            seq.done()
        Scheduler.wait(2, self._song.reset)

    def _restore_selected_state(self):
        # type: () -> None
        if SongDataManager.SELECTED_SCENE_INDEX is not None and SongDataManager.SELECTED_SCENE_INDEX < len(
                self._song.scenes):
            selected_scene = self._song.scenes[SongDataManager.SELECTED_SCENE_INDEX]
            selected_scene.select()
        if SongDataManager.SELECTED_TRACK_INDEX is not None and SongDataManager.SELECTED_TRACK_INDEX < len(
                list(self._song.all_simple_tracks)):
            selected_track = list(self._song.all_simple_tracks)[SongDataManager.SELECTED_TRACK_INDEX]
            selected_track.select()
        if SongDataManager.LAST_MANUALLY_STARTED_SCENE_INDEX is not None and SongDataManager.LAST_MANUALLY_STARTED_SCENE_INDEX < len(
                list(self._song.scenes)):
            scene = self._song.scenes[SongDataManager.LAST_MANUALLY_STARTED_SCENE_INDEX]
            if not SongDataManager.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION or SongDataManager.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION < scene.bar_length:
                Scene.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION = SongDataManager.LAST_MANUALLY_STARTED_SCENE_BAR_POSITION
            Scene.LAST_MANUALLY_STARTED_SCENE = scene

    def _get_startup_track(self):
        # type: () -> Optional[AbstractTrack]
        if Config.FOCUS_PROPHET_ON_STARTUP:
            first_prophet_track = next(self._song.prophet_tracks, None)
            if first_prophet_track:
                return first_prophet_track
            else:
                raise Protocol0Warning("Couldn't find prophet track")

        armed_tracks = self._song.armed_tracks
        if len(armed_tracks):
            return armed_tracks[0]

        if self._song.selected_track == self._song.master_track:
            return next(self._song.abstract_tracks)

        return None

    def scroll_tempo(self, go_next):
        # type: (bool) -> None
        increment = 1 if go_next else -1
        self._song.tempo += increment
