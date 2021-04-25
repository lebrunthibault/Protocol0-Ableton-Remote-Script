import collections

import Live
from typing import List, Optional, Dict, Any, Generator, Iterable

from a_protocol_0.interface.InterfaceState import InterfaceState
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Scene import Scene
from a_protocol_0.lom.SongActionMixin import SongActionMixin
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.AbstractTrackList import AbstractTrackList
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.utils.decorators import p0_subject_slot
from a_protocol_0.utils.utils import find_if


class Song(AbstractObject, SongActionMixin):
    def __init__(self, song, *a, **k):
        # type: (Live.Song.Song, Any, Any) -> None
        super(Song, self).__init__(*a, **k)
        self._song = song
        self._view = self._song.view  # type: Live.Song.Song.View

        # Global accessible objects / object mappings
        self.scenes = []  # type: List[Scene]
        self.live_track_to_simple_track = collections.OrderedDict()  # type: Dict[Live.Track.Track, SimpleTrack]
        self.clip_slots_by_live_live_clip_slot = {}  # type: Dict[Live.ClipSlot.ClipSlot, ClipSlot]

        self.errored = False
        self._is_playing_listener.subject = self._song

    def __call__(self):
        # type: () -> Live.Song.Song
        """ allows for self.song() behavior to extend other surface script classes """
        return self.parent.song()

    @p0_subject_slot("is_playing")
    def _is_playing_listener(self):
        # type: () -> None
        if len(self.scenes) and self.is_playing:
            self.selected_scene.notify_play()  # type: ignore

    # TRACKS

    @property
    def simple_tracks(self):
        # type: () -> Generator[SimpleTrack, Any, Any]
        return (track for track in self.live_track_to_simple_track.values() if track.is_active)

    @property
    def abstract_tracks(self):
        # type: () -> Iterable[AbstractTrack]
        for track in self.simple_tracks:
            if track == track.abstract_track.base_track:
                yield track.abstract_track

    @property
    def selected_track(self):
        # type: () -> SimpleTrack
        """ returns the SimpleTrack of the selected track, raises for master / return tracks """
        return self.live_track_to_simple_track[self.song._view.selected_track]

    @property
    def current_track(self):
        # type: () -> AbstractTrack
        return self.song.selected_track.abstract_track

    @property
    def scrollable_tracks(self):
        # type: () -> Iterable[AbstractTrack]
        return (track for track in self.abstract_tracks if track.is_visible)

    @property
    def selected_abstract_tracks(self):
        # type: () -> AbstractTrackList
        return AbstractTrackList(
            track.abstract_track for track in self.simple_tracks if track._track.is_part_of_selection
        )

    @property
    def selected_category_tracks(self):
        # type: () -> AbstractTrackList
        return AbstractTrackList(
            track
            for track in self.abstract_tracks
            if track.category.value.lower() == InterfaceState.SELECTED_TRACK_CATEGORY.value.lower()
        )

    # SCENES

    @property
    def selected_scene(self):
        # type: () -> Scene
        scene = find_if(lambda scene: scene._scene == self.song._view.selected_scene, self.scenes)
        assert scene
        return scene

    @selected_scene.setter
    def selected_scene(self, scene):
        # type: (Scene) -> None
        self.song._view.selected_scene = scene._scene

    # CLIP SLOTS

    @property
    def highlighted_clip_slot(self):
        # type: () -> Optional[ClipSlot]
        """ first look in track then in song """
        if self.song._view.highlighted_clip_slot in self.clip_slots_by_live_live_clip_slot:
            return self.clip_slots_by_live_live_clip_slot[self.song._view.highlighted_clip_slot]
        else:
            return None

    @highlighted_clip_slot.setter
    def highlighted_clip_slot(self, clip_slot):
        # type: (ClipSlot) -> None
        self.song._view.highlighted_clip_slot = clip_slot._clip_slot

    # CLIPS

    @property
    def selected_clip(self):
        # type: () -> Optional[Clip]
        return self.highlighted_clip_slot and self.highlighted_clip_slot.clip

    @selected_clip.setter
    def selected_clip(self, selected_clip):
        # type: (Clip) -> None
        self.highlighted_clip_slot = selected_clip.clip_slot

    @property
    def selected_parameter(self):
        # type: () -> Optional[DeviceParameter]
        all_parameters = [param for track in self.simple_tracks for param in track.device_parameters]
        return find_if(lambda p: p._device_parameter == self.song._view.selected_parameter, all_parameters)

    @property
    def is_playing(self):
        # type: () -> bool
        return self._song.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        self._song.is_playing = is_playing

    @property
    def metronome(self):
        # type: () -> float
        return self._song.metronome

    @metronome.setter
    def metronome(self, metronome):
        # type: (bool) -> None
        self._song.metronome = metronome

    @property
    def tempo(self):
        # type: () -> float
        return self._song.tempo

    @property
    def signature_denominator(self):
        # type: () -> int
        return self._song.signature_denominator

    def get_current_beats_song_time(self):
        # type: () -> Live.Song.BeatTime
        return self._song.get_current_beats_song_time()

    @property
    def clip_trigger_quantization(self):
        # type: () -> int
        return self._song.clip_trigger_quantization

    @clip_trigger_quantization.setter
    def clip_trigger_quantization(self, clip_trigger_quantization):
        # type: (int) -> None
        self._song.clip_trigger_quantization = clip_trigger_quantization
