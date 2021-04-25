import os

import Live
from typing import List, Optional, Dict, Any, Generator

from a_protocol_0.enums.TrackCategoryEnum import TrackCategoryEnum
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
from a_protocol_0.utils.utils import flatten


class Song(AbstractObject, SongActionMixin):
    def __init__(self, song, *a, **k):
        # type: (Live.Song.Song, Any, Any) -> None
        super(Song, self).__init__(*a, **k)
        self._song = song
        self._view = self._song.view  # type: Live.Song.Song.View
        self.scenes = []  # type: List[Scene]
        self.selected_track_category = TrackCategoryEnum.ALL  # type: TrackCategoryEnum
        self._selected_recording_time = "1 bar"  # type: str
        self.recording_bar_count = 1
        self.clip_slots = []  # type: List[ClipSlot]
        self.clip_slots_by_live_live_clip_slot = {}  # type: Dict[Live.ClipSlot.ClipSlot, ClipSlot]
        self.errored = False
        # only one scene can be set to looping : it should be the scene we are working on ("soloing")
        self.looping_scene = None  # type: Optional[Scene]
        self.playing_scene = None  # type: Optional[Scene]

        # NB: for an unknown reason clip.view.show_envelope does not always show the envelope
        # when the button was not clicked. As a workaround we click it the first time
        self.clip_envelope_show_box_clicked = False

        self._is_playing_listener.subject = self._song

        # with this set to True, the script is going to rename more aggressively
        self.fix_outdated_sets = str(os.getenv("FIX_OUTDATED_SETS")).lower() == "true"  # type: bool

    def __call__(self):
        # type: () -> Live.Song.Song
        """ allows for self.song() behavior to extend other surface script classes """
        return self.parent.song()

    @p0_subject_slot("is_playing")
    def _is_playing_listener(self):
        # type: () -> None
        if len(self.scenes) and self.is_playing:
            self.selected_scene.notify_play()  # type: ignore

    @property
    def selected_track(self):
        # type: () -> SimpleTrack
        """ returns the SimpleTrack of the selected track, raises for master / return tracks """
        return self.parent.songManager.live_track_to_simple_track[self.song._view.selected_track]

    @property
    def current_track(self):
        # type: () -> AbstractTrack
        return self.song.selected_track.abstract_track

    @property
    def simple_tracks(self):
        # type: () -> Generator[SimpleTrack, Any, Any]
        return (track for track in self.parent.songManager.live_track_to_simple_track.values() if track.is_active)

    @property
    def abstract_tracks(self):
        # type: () -> List[AbstractTrack]
        abstract_tracks = []  # type: List[AbstractTrack]
        for track in self.simple_tracks:
            if len(abstract_tracks) == 0 or track.abstract_track != abstract_tracks[-1]:
                abstract_tracks.append(track.abstract_track)
        return abstract_tracks

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

    @property
    def scrollable_tracks(self):
        # type: () -> Generator[AbstractTrack, Any, Any]
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
            if track.category.value.lower() == self.selected_track_category.value.lower()
        )

    @property
    def highlighted_clip_slot(self):
        # type: () -> ClipSlot
        """ first look in track then in song """
        return self.clip_slots_by_live_live_clip_slot[self.song._view.highlighted_clip_slot]

    @highlighted_clip_slot.setter
    def highlighted_clip_slot(self, clip_slot):
        # type: (ClipSlot) -> None
        self.song._view.highlighted_clip_slot = clip_slot._clip_slot

    @property
    def selected_clip(self):
        # type: () -> Optional[Clip]
        return self.highlighted_clip_slot.clip

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

    @property
    def clips(self):
        # type: () -> List[Clip]
        """ All clips of the set flattened """
        return flatten([t.clips for t in self.simple_tracks])
