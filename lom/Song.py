import Live
from typing import List, Optional, Dict

from _Framework.Util import find_if
from a_protocol_0.enums.AbstractEnum import AbstractEnum
from a_protocol_0.enums.TrackCategoryEnum import TrackCategoryEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.Scene import Scene
from a_protocol_0.lom.SongActionMixin import SongActionMixin
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.simple_track.AudioBusTrack import AudioBusTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.utils import flatten


class Song(SongActionMixin, AbstractObject):
    AUDIO_BUS_TRACK_INDEX = 0  # audio bus is supposed to be the first track

    def __init__(self, song, *a, **k):
        # type: (Live.Song.Song) -> None
        super(Song, self).__init__(*a, **k)
        self._song = song
        self._view = self._song.view  # type: Live.Song.Song.View
        self.scenes = []  # type: List[Scene]
        self.simple_tracks = []  # type: List[SimpleTrack]
        self.abstract_tracks = []  # type: List[AbstractTrack]
        self.abstract_group_tracks = []  # type: List[AbstractGroupTrack]
        self.selected_track = None  # type: SimpleTrack
        self.current_track = None  # type: AbstractTrack
        self.master_track = self._song.master_track  # type: Live.Track.Track
        self.selected_track_category = TrackCategoryEnum.ALL  # type: AbstractEnum
        self.selected_recording_time = "1 bar"
        self.recording_bar_count = 1
        self.solo_playing_tracks = []  # type: List[AbstractTrack]
        self.solo_stopped_tracks = []  # type: List[AbstractTrack]
        self.clip_slots = []  # type: List[ClipSlot]
        self.clip_slots_by_live_live_clip_slot = {}  # type: Dict[int, Live.ClipSlot.ClipSlot]
        self.errored = False

    def __call__(self):
        # type: () -> Live.Song.Song
        """ allows for self.song() behavior to extend other surface script classes """
        return self.parent.song()

    def handle_error(self, message):
        self.reset()
        seq = Sequence(bypass_errors=True, silent=True)
        self.errored = True
        seq.add(wait=100)
        seq.add(lambda: setattr(self, "errored", False))
        return seq.done()

    @property
    def selected_scene(self):
        # type: () -> Scene
        return find_if(lambda scene: scene._scene == self.song._view.selected_scene, self.scenes)

    @selected_scene.setter
    def selected_scene(self, scene):
        # type: (Scene) -> None
        self.song._view.selected_scene = scene._scene

    def next_track(self, increment=1, base_track=None):
        # type: (int, SimpleTrack) -> SimpleTrack
        base_track = base_track or self.selected_track
        if base_track is None:
            raise Protocol0Error("You called next_track before selected_track computation")
        return self.simple_tracks[(base_track.index + increment) % len(self.simple_tracks)]

    @property
    def scrollable_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.simple_tracks if track.is_visible and track.is_scrollable]

    @property
    def root_tracks(self):
        # type: () -> List[SimpleTrack]
        """ top tracks """
        return [track for track in self.simple_tracks if not track.group_track]

    @property
    def simple_group_tracks(self):
        # type: () -> List[SimpleTrack]
        return [track for track in self.simple_tracks if len(track.sub_tracks)]

    @property
    def selected_abstract_tracks(self):
        # type: () -> List[AbstractTrack]
        return [self.parent.songManager.get_current_track(track) for track in self.simple_tracks if
                track._track.is_part_of_selection]

    @property
    def selected_category_tracks(self):
        # type: () -> List[AbstractTrack]
        if self.selected_track_category == TrackCategoryEnum.ALL:
            return self.simple_tracks
        return [track for track in self.abstract_tracks if
                track.category.lower() == self.selected_track_category.value.lower()]

    @property
    def audio_bus_track(self):
        # type: () -> AudioBusTrack
        audio_bus_index = self.song.AUDIO_BUS_TRACK_INDEX
        audio_bus_track = self.song.simple_tracks[audio_bus_index]
        assert isinstance(audio_bus_track, AudioBusTrack), "set should contain an audio bus track at index " + audio_bus_index
        return audio_bus_track

    @property
    def highlighted_clip_slot(self):
        # type: () -> Optional[ClipSlot]
        """ first look in track then in song """
        return find_if(lambda cs: cs._clip_slot == self.song._view.highlighted_clip_slot,
                       self.selected_track.clip_slots) or find_if(
            lambda cs: cs._clip_slot == self.song._view.highlighted_clip_slot,
            [cs for track in self.song.simple_tracks for cs in track.clip_slots])

    @highlighted_clip_slot.setter
    def highlighted_clip_slot(self, clip_slot):
        # type: (ClipSlot) -> None
        self.song._view.highlighted_clip_slot = clip_slot._clip_slot

    @property
    def highlighted_clip(self):
        # type: () -> Optional[Clip]
        return self.highlighted_clip_slot.clip if self.highlighted_clip_slot and self.highlighted_clip_slot.has_clip else None

    @property
    def selected_parameter(self):
        # type: () -> Optional[DeviceParameter]
        return find_if(lambda p: p._device_parameter == self.song._view.selected_parameter, [param for track in self.simple_tracks for param in track.device_parameters])

    @property
    def is_playing(self):
        return self._song.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
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

    @property
    def playing_clips(self):
        # type: () -> List[Clip]
        return [t.playable_clip for t in self.simple_tracks if t.is_playing and t.playable_clip and t.playable_clip.is_playing]

    @property
    def has_solo_selection(self):
        return len(self.solo_playing_tracks) != 0
