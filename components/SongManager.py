import collections
from plistlib import Dict
from typing import Optional, Any

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class SongManager(AbstractControlSurfaceComponent):
    __subject_events__ = ('selected_track', 'scene_list', 'added_track')

    def __init__(self, *a, **k):
        super(SongManager, self).__init__(*a, **k)
        self._live_track_to_simple_track = collections.OrderedDict()  # type: Dict[Any, SimpleTrack]
        self._simple_track_to_external_synth_track = collections.OrderedDict()  # type: Dict[SimpleTrack, ExternalSynthTrack]
        self._tracks_listener.subject = self.song._song
        self.update_highlighted_clip_slot = True

    def init_song(self):
        self._tracks_listener()
        self._highlighted_clip_slot = self.song.highlighted_clip_slot
        self._highlighted_clip_slot_poller()
        self.song.reset()

    def on_selected_track_changed(self):
        self._set_current_track()
        self.parent.clyphxNavigationManager.show_track_view()
        # noinspection PyUnresolvedReferences
        self.notify_selected_track()

    def on_scene_list_changed(self):
        # noinspection PyUnresolvedReferences
        self.notify_scene_list()

    @subject_slot("tracks")
    def _tracks_listener(self):
        # type: () -> Optional[SimpleTrack]
        if len(self.song.tracks) and len(self.song._song.tracks) > len(self.song.tracks):
            # noinspection PyUnresolvedReferences
            self.notify_added_track()

        self.song.tracks = []
        self.song.abstract_group_tracks = []

        for i, track in enumerate(list(self.song._song.tracks)):
            simple_track = self.parent.trackManager.create_simple_track(track=track, index=i)
            self._live_track_to_simple_track[track] = simple_track
            self.song.tracks.append(simple_track)

        # link sub_tracks
        for track in self.song.tracks:  # type: SimpleTrack
            if track._track.group_track:
                track.group_track = self._get_simple_track(track._track.group_track)
                track.group_track.sub_tracks.append(track)
                track.group_tracks = [track.group_track] + track.group_track.group_tracks

        # generate group tracks
        for track in self.song.tracks:  # type: SimpleTrack
            if track.is_external_synth_track:
                self.song.abstract_group_tracks.append(ExternalSynthTrack(track=track, index=track.index))
            if track.is_automation_group:

        self._simple_track_to_external_synth_track = {}
        for es_track in self.song.abstract_group_tracks:
            self._simple_track_to_external_synth_track.update(
                {es_track.base_track: es_track, es_track.midi: es_track, es_track.audio: es_track})

        self._set_current_track()
        self.song.clip_slots = [cs for track in self.song.tracks for cs in track.clip_slots]
        self.parent.log_info("SongManager : mapped tracks")

    def _highlighted_clip_slot_poller(self):
        # type: () -> None
        if self.song.highlighted_clip_slot != self._highlighted_clip_slot:
            self._highlighted_clip_slot = self.song.highlighted_clip_slot
            if self.song.highlighted_clip_slot and self.song.highlighted_clip_slot.has_clip:
                # self.song.highlighted_clip_slot.track._clip_notes_listener.subject = self.song.highlighted_clip_slot.clip._clip
                self.parent.push2Manager.update_clip_grid_quantization()
        self.parent.defer(self._highlighted_clip_slot_poller)

    def _update_highlighted_clip_slot(self):
        """ auto_update highlighted clip slot to match the playable clip """
        if self.update_highlighted_clip_slot:
            track = self.song.selected_track
            if track and track.is_visible and track.playable_clip and self.song.highlighted_clip_slot == \
                    track.clip_slots[0]:
                self.song.highlighted_clip_slot = track.playable_clip.clip_slot
        self.update_highlighted_clip_slot = True

    def _get_simple_track(self, track, default=None):
        # type: (Any, Optional[SimpleTrack]) -> Optional[SimpleTrack]
        """ default is useful when the _ableton_track_to_simple_track is not built yet """
        if not track:
            return None
        if isinstance(track, AbstractTrack):
            raise Exception("Expected Live track, got AbstractTrack instead")

        if track == self.song._song.master_track or track in self.song._song.return_tracks:
            return default
        if track not in self._live_track_to_simple_track.keys():
            if default:
                return default
            raise Exception("_get_simple_track mismatch on %s" % track.name)

        return self._live_track_to_simple_track[track]

    def _set_current_track(self):
        self.song.selected_track = self._get_simple_track(self.song._view.selected_track) or self.song.tracks[0]
        self.song.current_track = self.get_current_track(self.song.selected_track)

    def get_current_track(self, track):
        # type: (SimpleTrack) -> AbstractTrack
        if track in self._simple_track_to_external_synth_track:
            return self._simple_track_to_external_synth_track[track]
        elif track in self._wrapped_group_tracks:
            return self._wrapped_group_tracks[track]
        else:
            return track
