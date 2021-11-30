import collections

from typing import Any, List, Optional, Type

import Live
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.devices.InstrumentProphet import InstrumentProphet
from protocol0.enums.AbletonSessionTypeEnum import AbletonSessionTypeEnum
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.SongLoadStateEnum import SongLoadStateEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.Scene import Scene
from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
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
        self.song.song_load_state = SongLoadStateEnum.LOADING
        self._select_startup_track()
        if InterfaceState.ABLETON_SESSION_TYPE != AbletonSessionTypeEnum.PROFILING:
            self.parent.wait(2, self.song.reset)

    def _select_startup_track(self):
        # type: () -> None
        if InterfaceState.FOCUS_PROPHET_ON_STARTUP:
            first_prophet_track = next(
                (abt for abt in self.song.abstract_tracks if isinstance(abt.instrument, InstrumentProphet)), None)
            if first_prophet_track:
                self.song.select_track(first_prophet_track)
                self.parent.wait(2, first_prophet_track.arm)
                return None
            else:
                self.parent.show_message("Couldn't find prophet track")

        if len(self.song.armed_tracks):
            self.song.select_track(self.song.armed_tracks[0])

        if self.song.selected_track == self.song.master_track:
            self.song.select_track(next(self.song.abstract_tracks))

    @handle_error
    def on_scene_list_changed(self):
        # type: () -> None
        self.parent.sceneBeatScheduler.clear()
        self.tracks_listener()
        self.parent.defer(lambda: [scene.refresh_appearance() for scene in self.song.scenes])
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
        has_added_tracks = 0 < previous_simple_track_count < len(self.song._song.tracks)

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
        self.template_dummy_clip = None  # type: Optional[AudioClip]
        # instantiate set tracks

        for track in list(self.song._song.tracks) + list(self.song._song.return_tracks):
            self.generate_simple_track(track=track)

        if self.song.usamo_track is None and self.song.song_load_state != SongLoadStateEnum.LOADED:
            self.parent.log_warning("Usamo track is not present")

        self.song.master_track = self.generate_simple_track(track=self.song._song.master_track)

        # Refresh track mapping
        self.song.live_track_to_simple_track = collections.OrderedDict()
        for track in self._simple_tracks:
            self.song.live_track_to_simple_track[track._track] = track

        # Store clip_slots mapping. track and scene changes trigger a song remapping so it's fine
        self.song.clip_slots_by_live_live_clip_slot = {
            clip_slot._clip_slot: clip_slot for track in self.song.simple_tracks for clip_slot in track.clip_slots
        }

    def generate_simple_track(self, track, cls=None):
        # type: (Live.Track.Track, Optional[Type[SimpleTrack]]) -> SimpleTrack
        simple_track = self.parent.trackManager.instantiate_simple_track(track=track, cls=cls)
        self._register_simple_track(simple_track)
        simple_track.post_init()

        if self.song.usamo_track is None:
            if simple_track.get_device_from_enum(DeviceEnum.USAMO):
                self.song.usamo_track = simple_track

        if simple_track.name == SimpleInstrumentBusTrack.DEFAULT_NAME and len(simple_track.clips):
            self.song.template_dummy_clip = simple_track.clips[0]

        return simple_track

    def _register_simple_track(self, simple_track):
        # type: (SimpleTrack) -> None
        # rebuild sub_tracks
        simple_track.sub_tracks = []

        # handling replacement of a SimpleTrack by another
        if simple_track._track in self.song.live_track_to_simple_track:
            previous_simple_track = self.song.live_track_to_simple_track[simple_track._track]
            if previous_simple_track != simple_track:
                self._remove_outdated_simple_track(previous_simple_track, simple_track)

        # registering
        self.song.live_track_to_simple_track[simple_track._track] = simple_track
        self._simple_tracks.append(simple_track)

    def _remove_outdated_simple_track(self, previous_simple_track, new_simple_track):
        # type: (SimpleTrack, SimpleTrack) -> None
        """ disconnecting and removing from SimpleTrack group track and abstract_group_track """
        previous_simple_track.disconnect()

        # group_track
        group_track = previous_simple_track.group_track
        if previous_simple_track in group_track.sub_tracks:
            group_track.sub_tracks.remove(previous_simple_track)

        # abstract_group_track
        abstract_group_track = group_track.abstract_group_track
        if abstract_group_track and previous_simple_track in abstract_group_track.sub_tracks:
            abstract_group_track.sub_tracks.remove(previous_simple_track)

        # deferred dummy track instantiation
        if previous_simple_track in self._simple_tracks:
            self._simple_tracks.remove(previous_simple_track)

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

        new_scenes = []

        # get the right scene or instantiate new scenes
        for live_scene in live_scenes:
            if live_scene in scene_mapping:
                scene = scene_mapping[live_scene]
            else:
                scene = Scene(live_scene)
            scene.link_clip_slots_and_clips()

            new_scenes.append(scene)

        self.song.scenes[:] = new_scenes

        if has_added_scene and self.song.selected_scene and self.song.is_playing:
            # noinspection PyUnresolvedReferences
            self.parent.defer(self.song.selected_scene.fire)

    def _highlighted_clip_slot_poller(self):
        # type: () -> None
        if self.song.highlighted_clip_slot and self.song.highlighted_clip_slot != self._highlighted_clip_slot:
            self._highlighted_clip_slot = self.song.highlighted_clip_slot
            if self.song.highlighted_clip_slot.clip:
                # self.parent.push2Manager.update_clip_grid_quantization()
                self._highlighted_clip_slot.clip._on_selected()
        self.parent.wait(10, self._highlighted_clip_slot_poller)

    def scroll_tempo(self, go_next):
        # type: (bool) -> None
        increment = 1 if go_next else -1
        self.song.tempo += increment
