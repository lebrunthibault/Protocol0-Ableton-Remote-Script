import collections

from typing import Any, List, Optional

import Live
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.config import Config
from protocol0.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.lom.Scene import Scene
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.utils.decorators import handle_error, p0_subject_slot


class SongManager(AbstractControlSurfaceComponent):
    __subject_events__ = ("selected_track", "added_track")

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SongManager, self).__init__(*a, **k)
        self.tracks_listener.subject = self.song._song
        # keeping a list of instantiated tracks because we cannot access
        # song.live_track_to_simple_track when tracks are deleted
        self._simple_tracks = []  # type: List[SimpleTrack]
        self._highlighted_clip_slot = None  # type: Optional[ClipSlot]

    def init_song(self):
        # type: () -> None
        self.tracks_listener()
        # self._highlighted_clip_slot = self.song.highlighted_clip_slot
        # self._highlighted_clip_slot_poller()
        if Config.ABLETON_SESSION_TYPE != AbletonSessionTypeEnum.PROFILING:
            self.song.reset()
        self.song.is_loading = False
        if len(self.song.armed_tracks):
            self.song.select_track(self.song.armed_tracks[0])
        elif self.song.selected_track == self.song.master_track:
            self.song.select_track(next(self.song.abstract_tracks))

    @handle_error
    def on_scene_list_changed(self):
        # type: () -> None
        self.parent.sceneBeatScheduler.clear()
        self.tracks_listener()
        self.parent.defer(self.parent.setFixerManager.refresh_scenes_appearance)
        if self.song.playing_scene:
            self.song.playing_scene.schedule_next_scene_launch()

    @handle_error
    def on_selected_track_changed(self):
        # type: () -> None
        """ not for master and return tracks """
        if len(self.song.live_track_to_simple_track):
            # noinspection PyUnresolvedReferences
            self.notify_selected_track()

    @p0_subject_slot("tracks")
    @handle_error
    def tracks_listener(self):
        # type: () -> None
        # Check if tracks were added
        previous_simple_track_count = len(list(self._simple_tracks))
        has_added_tracks = previous_simple_track_count and len(self.song._song.tracks) > previous_simple_track_count

        self._generate_simple_tracks()
        self._generate_abstract_group_tracks()
        self._generate_scenes()

        if has_added_tracks and self.song.selected_track:
            # noinspection PyUnresolvedReferences
            self.notify_added_track()

        self._simple_tracks = list(self.song.simple_tracks)
        # self.parent.defer(partial(self.parent.setFixerManager.refresh_set_appearance, log=False))
        self.parent.log_debug("SongManager : mapped tracks")
        # noinspection PyUnresolvedReferences
        self.notify_selected_track()  # trigger other components

    def _generate_simple_tracks(self):
        # type: () -> None
        """ instantiate SimpleTracks (including return / master, that are marked as inactive) """
        self._simple_tracks[:] = []
        self.song.usamo_track = None
        # instantiate set tracks
        for track in list(self.song._song.tracks) + list(self.song._song.return_tracks):
            self._generate_simple_track(track=track)

        if self.song.usamo_track is None:
            self.parent.log_warning("Usamo track is not present")

        self.song.master_track = self._generate_simple_track(track=self.song._song.master_track)

        # Refresh track mapping
        self.song.live_track_to_simple_track = collections.OrderedDict()
        for track in self._simple_tracks:
            self.song.live_track_to_simple_track[track._track] = track

        # Store clip_slots mapping. track and scene changes trigger a song remapping so it's fine
        self.song.clip_slots_by_live_live_clip_slot = {
            clip_slot._clip_slot: clip_slot for track in self.song.simple_tracks for clip_slot in track.clip_slots
        }

    def _generate_simple_track(self, track):
        # type: (Live.Track.Track) -> SimpleTrack
        simple_track = self.parent.trackManager.instantiate_simple_track(track=track)
        usamo = simple_track.get_device_from_enum(DeviceEnum.USAMO)
        if usamo:
            self.song.usamo_track = simple_track

        if simple_track.name == Config.INSTRUMENT_BUS_TRACK_NAME and len(simple_track.clips):
            self.song.template_dummy_clip = simple_track.clips[0]

        self.song.live_track_to_simple_track[track] = simple_track
        self._simple_tracks.append(simple_track)
        return simple_track

    def _generate_abstract_group_tracks(self):
        # type: () -> None
        # 2nd pass : instantiate AbstractGroupTracks
        for track in self.song.simple_tracks:
            if track.is_foldable:
                self.parent.trackManager.instantiate_abstract_group_track(track)

    def _generate_scenes(self):
        # type: () -> None
        live_scenes = self.song._song.scenes
        has_added_scene = len(self.song.scenes) and len(live_scenes) > len(self.song.scenes)

        # disconnect removed scenes
        for scene in self.song.scenes:
            if scene._scene not in live_scenes:
                scene.disconnect()

        # create a dict access from live scenes
        scene_mapping = collections.OrderedDict()
        for scene in self.song.scenes:
            scene_mapping[scene._scene] = scene

        self.song.scenes[:] = []

        # get the right scene or instantiate new scenes
        for live_scene in live_scenes:
            if live_scene in scene_mapping:
                scene = scene_mapping[live_scene]
            else:
                scene = Scene(live_scene)
            scene.link_clip_slots_and_clips()

            self.song.scenes.append(scene)

        if has_added_scene and self.song.selected_scene and self.song.is_playing:
            # noinspection PyUnresolvedReferences
            self.parent.defer(self.song.selected_scene.fire)

    def _highlighted_clip_slot_poller(self):
        # type: () -> None
        if self.song.highlighted_clip_slot and self.song.highlighted_clip_slot != self._highlighted_clip_slot:
            self._highlighted_clip_slot = self.song.highlighted_clip_slot
            if self.song.highlighted_clip_slot.clip:
                self.parent.push2Manager.update_clip_grid_quantization()
                self._highlighted_clip_slot.clip._on_selected()
        self.parent.wait(10, self._highlighted_clip_slot_poller)

    def scroll_tempo(self, go_next):
        # type: (bool) -> None
        increment = 1 if go_next else -1
        self.song.tempo += increment
