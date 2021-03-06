import Live
from typing import Any, List, Optional

from _Framework.Util import find_if
from a_protocol_0.consts import TRACK_CATEGORY_ALL
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.SongActionMixin import SongActionMixin
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.lom.track.simple_track.SimpleGroupTrack import SimpleGroupTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import is_change_deferrable
from a_protocol_0.utils.utils import flatten


class Song(SongActionMixin, AbstractObject):
    def __init__(self, song, *a, **k):
        # type: (Live.Song.Song) -> None
        super(Song, self).__init__(*a, **k)
        self._song = song
        self._view = self._song.view  # type: Live.Song.Song.View
        self.simple_tracks = []  # type: List[SimpleTrack]
        self.abstract_tracks = []  # type: List[AbstractTrack]
        self.abstract_group_tracks = []  # type: List[AbstractGroupTrack]
        self.selected_track = None  # type: SimpleTrack
        self.current_track = None  # type: AbstractTrack
        self.master_track = self._song.master_track  # type: Live.Track.Track
        self.selected_track_category = TRACK_CATEGORY_ALL
        self.selected_recording_time = "1 bar"
        self.recording_bar_count = 1
        self.solo_playing_tracks = []  # type: List[AbstractTrack]
        self.solo_stopped_tracks = []  # type: List[AbstractTrack]
        self.errored = False

    def __call__(self):
        # type: () -> Live.Song.Song
        """ allows for self.song() behavior to extend other surface script classes """
        return self.parent.song()

    def handle_error(self):
        seq = Sequence(bypass_errors=True, debug=False)
        self.errored = True
        self.parent.keyboardShortcutManager.focus_logs()
        seq.add(wait=1)
        seq.add(lambda: setattr(self, "errored", False))
        return seq.done()

    @property
    def scenes(self):
        # type: () -> List[Live.Scene.Scene]
        return list(self._song.scenes)

    @property
    def selected_scene(self):
        # type: () -> Live.Scene.Scene
        return self.song._view.selected_scene

    @property
    def selected_scene_index(self):
        # type: () -> Live.Scene.Scene
        return self.song.scenes.index(self.song._view.selected_scene)

    @selected_scene.setter
    def selected_scene(self, selected_scene):
        # type: (Live.Scene.Scene) -> None
        self.song._view.selected_scene = selected_scene

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
        # type: () -> List[SimpleGroupTrack]
        return [track for track in self.simple_tracks if isinstance(track, SimpleGroupTrack)]

    @property
    def selected_tracks(self):
        # type: () -> List[AbstractTrack]
        return [self.parent.songManager.get_current_track(track) for track in self.simple_tracks if
                track._track.is_part_of_selection]

    @property
    def selected_category_tracks(self):
        # type: () -> List[AbstractTrack]
        if self.selected_track_category == TRACK_CATEGORY_ALL:
            return self.simple_tracks
        return [track for track in self.abstract_tracks if
                track.category.lower() == self.selected_track_category.lower()]

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
    @is_change_deferrable
    def metronome(self, metronome):
        # type: (bool) -> None
        self._song.metronome = metronome

    @property
    def clip_trigger_quantization(self):
        # type: () -> int
        return self._song.clip_trigger_quantization

    @clip_trigger_quantization.setter
    def clip_trigger_quantization(self, clip_trigger_quantization):
        # type: (int) -> None
        self._song.clip_trigger_quantization = clip_trigger_quantization

    def get_clip(self, clip):
        # type: (Live.Clip.Clip) -> Optional[Clip]
        return find_if(lambda c: c._clip == clip, self.clips)

    @property
    def clips(self):
        # type: () -> List[Clip]
        clips = [t.clips for t in self.simple_tracks]
        return flatten(clips)

    @property
    def playing_clips(self):
        # type: () -> List[Clip]
        return [t.playable_clip for t in self.simple_tracks if t.is_playing and t.playable_clip and t.playable_clip.is_playing]

    @property
    def has_solo_selection(self):
        return len(self.solo_playing_tracks) != 0
