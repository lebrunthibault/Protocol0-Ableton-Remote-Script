from typing import Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.Scene import Scene
from a_protocol_0.utils.decorators import p0_subject_slot, has_callback_queue, handle_error


class SongManager(AbstractControlSurfaceComponent):
    __subject_events__ = ("selected_track", "added_track")

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SongManager, self).__init__(*a, **k)
        self._tracks_listener.subject = self.song._song

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
        """ not for master and return tracks """
        # noinspection PyUnresolvedReferences
        self.notify_selected_track()

    @handle_error
    def on_scene_list_changed(self):
        # type: () -> None
        self._tracks_listener()

    @p0_subject_slot("tracks")
    @handle_error
    def _tracks_listener(self):
        # type: () -> None
        self.parent.log_debug("SongManager : start mapping tracks")

        has_added_tracks = len(list(self.song.simple_tracks)) and len(self.song._song.tracks) > len(
            list(self.song.simple_tracks)
        )

        # 1. Instantiate SimpleTracks (including return / master, that are marked as inactive)
        song_tracks = (
            list(self.song._song.tracks) + list(self.song._song.return_tracks) + [self.song._song.master_track]
        )
        for track in song_tracks:
            simple_track = self.parent.trackManager.instantiate_simple_track(track=track)
            self.song.live_track_to_simple_track[track] = simple_track

        # 2. Remove deleted tracks from the map by checking stale live tracks
        for track in self.song.live_track_to_simple_track.keys():
            if track not in song_tracks:
                del self.song.live_track_to_simple_track[track]

        # 3. Instantiate AbstractGroupTracks
        for track in self.song.simple_tracks:
            if track.is_foldable:
                self.parent.trackManager.instantiate_abstract_group_track(track)

        # 4. Store clip_slots mapping. track and scene changes trigger a song remapping so it's fine
        self.song.clip_slots_by_live_live_clip_slot = {
            clip_slot._clip_slot: clip_slot for track in self.song.simple_tracks for clip_slot in track.clip_slots
        }

        # 5. Create Scenes
        self.song.scenes = [Scene(scene) for scene in list(self.song._song.scenes)]

        # 5. Handle added tracks
        if has_added_tracks and self.song.selected_track:
            # noinspection PyUnresolvedReferences
            self.notify_added_track()

        self.parent.log_debug("SongManager : mapped tracks")
        # noinspection PyUnresolvedReferences
        self.notify_selected_track()
        self.parent.log_debug("")

    def _highlighted_clip_slot_poller(self):
        # type: () -> None
        if self.song.highlighted_clip_slot and self.song.highlighted_clip_slot != self._highlighted_clip_slot:
            self._highlighted_clip_slot = self.song.highlighted_clip_slot
            if self.song.highlighted_clip_slot.clip:
                self.parent.push2Manager.update_clip_grid_quantization()
                self._highlighted_clip_slot.clip._on_selected()
        self.parent.schedule_message(1, self._highlighted_clip_slot_poller)
