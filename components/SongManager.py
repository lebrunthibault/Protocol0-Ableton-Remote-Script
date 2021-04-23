import collections

import Live
from typing import Optional, Any, Dict

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.Scene import Scene
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.utils.decorators import p0_subject_slot, has_callback_queue, retry, defer, handle_error
from a_protocol_0.utils.utils import flatten


class SongManager(AbstractControlSurfaceComponent):
    __subject_events__ = ("selected_track", "scene_list", "added_track")

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SongManager, self).__init__(*a, **k)
        self.live_track_to_simple_track = collections.OrderedDict()  # type: Dict[Any, SimpleTrack]
        self.simple_track_to_abstract_group_track = (
            collections.OrderedDict()
        )  # type: Dict[SimpleTrack, AbstractGroupTrack]
        self._tracks_listener.subject = self.song._song
        self.update_highlighted_clip_slot = True  # type: bool
        self.abstract_group_track_creation_in_progress = False  # type: bool

    @defer
    def init_song(self):
        # type: () -> None
        self.on_scene_list_changed()
        self._highlighted_clip_slot = self.song.highlighted_clip_slot
        self._highlighted_clip_slot_poller()
        self.song.reset()

    @has_callback_queue()
    @handle_error
    def on_selected_track_changed(self):
        # type: () -> None
        self._set_current_track()
        # noinspection PyUnresolvedReferences
        self.notify_selected_track()

    @handle_error
    def on_scene_list_changed(self):
        # type: () -> None
        self._tracks_listener()
        # noinspection PyUnresolvedReferences
        self.notify_scene_list()
        self.song.scenes = [Scene(scene, index) for index, scene in enumerate(list(self.song._song.scenes))]

    @p0_subject_slot("tracks")
    @handle_error
    def _tracks_listener(self):
        # type: () -> None
        self.parent.log_debug("SongManager : start mapping tracks")

        added_track = len(self.song.simple_tracks) and len(self.song._song.tracks) > len(self.song.simple_tracks)

        self.song.simple_tracks = self.song.abstract_group_tracks = []
        self.simple_track_to_abstract_group_track = {}

        # 1. Generate simple tracks
        for i, track in enumerate(list(self.song._song.tracks)):
            simple_track = self.parent.trackManager.instantiate_simple_track(track=track, index=i)
            self.song.simple_tracks.append(simple_track)
            self.live_track_to_simple_track[track] = simple_track

        # deleted remove tracks from the map
        for track, simple_track in self.live_track_to_simple_track.items():
            if simple_track not in self.song.simple_tracks:
                del self.live_track_to_simple_track[track]

        # 2. Generate abstract group tracks
        self.song.abstract_group_tracks = [
            self.parent.trackManager.instantiate_abstract_group_track(track) for track in self.song.simple_group_tracks
        ]

        # 3. Creating a mapping of SimpleTrack to AbstractGroupTrack
        for abstract_group_track in self.song.abstract_group_tracks:
            for abstract_group_sub_track in abstract_group_track.selection_tracks:
                self.simple_track_to_abstract_group_track.update({abstract_group_sub_track: abstract_group_track})

        # 4. Populate abstract_tracks property
        independent_simple_tracks = set(self.song.simple_tracks) - set(self.simple_track_to_abstract_group_track.keys())
        self.song.abstract_tracks = list(independent_simple_tracks) + self.song.abstract_group_tracks
        self.song.abstract_tracks.sort(key=lambda t: t.index)

        # 5. Set the currently selected track
        self._set_current_track()

        # 6. Store clip_slots. track and scene changes trigger a song remapping so it's fine
        self.song.clip_slots = flatten([track.clip_slots for track in self.song.simple_tracks])
        self.song.clip_slots_by_live_live_clip_slot = {
            clip_slot._clip_slot: clip_slot for clip_slot in self.song.clip_slots
        }

        # 7 handle added tracks
        if added_track and self.song.selected_track:
            added_track_index = self.song.simple_tracks.index(self.song.selected_track)
            if (
                added_track_index > 0
                and self.song.simple_tracks[added_track_index - 1].name == self.song.selected_track.name
            ):
                self.song.current_track._is_duplicated = True
            # noinspection PyUnresolvedReferences
            self.notify_added_track()

        self.parent.log_debug("SongManager : mapped tracks")
        self.parent.log_debug("")

    def _highlighted_clip_slot_poller(self):
        # type: () -> None
        if self.song.highlighted_clip_slot != self._highlighted_clip_slot:
            self._highlighted_clip_slot = self.song.highlighted_clip_slot
            if self.song.highlighted_clip_slot and self.song.highlighted_clip_slot.clip:
                self.parent.push2Manager.update_clip_grid_quantization()
                self._highlighted_clip_slot.clip._on_selected()
        self.parent.schedule_message(1, self._highlighted_clip_slot_poller)

    def _update_highlighted_clip_slot(self):
        # type: () -> None
        """ auto_update highlighted clip slot to match the playable clip """
        if self.update_highlighted_clip_slot:
            track = self.song.selected_track
            if track and track.is_visible and track.playable_clip and track.clip_slots[0].is_selected:
                pass
                # self.song.highlighted_clip_slot = track.playable_clip.clip_slot
        self.update_highlighted_clip_slot = True

    def _get_simple_track(self, track, default=None):
        # type: (Live.Track.Track, Optional[SimpleTrack]) -> SimpleTrack
        """ default is useful when the _ableton_track_to_simple_track is not built yet """
        if track == self.song._song.master_track or track in self.song._song.return_tracks:
            assert default
            return default

        assert len(self.live_track_to_simple_track.keys()), "live_track_to_simple_track is empty"
        assert track in self.live_track_to_simple_track.keys(), "_get_simple_track mismatch on %s" % track.name

        return self.live_track_to_simple_track[track]

    @retry(3)
    def _set_current_track(self):
        # type: () -> None
        self.song.selected_track = self._get_simple_track(self.song._view.selected_track, self.song.simple_tracks[0])
        self.song.current_track = self.get_current_track(self.song.selected_track)

    def get_current_track(self, track):
        # type: (SimpleTrack) -> AbstractTrack
        if track in self.simple_track_to_abstract_group_track:
            return self.simple_track_to_abstract_group_track[track]
        else:
            return track
