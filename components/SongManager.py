from __future__ import with_statement

import collections
from plistlib import Dict
from typing import Optional, Any

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import EXTERNAL_SYNTH_NAMES
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class SongManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(SongManager, self).__init__(*a, **k)
        self._live_track_to_simple_track = collections.OrderedDict()  # type: Dict[Any, SimpleTrack]
        self._simple_track_to_external_synth_track = collections.OrderedDict()  # type: Dict[SimpleTrack, ExternalSynthTrack]
        self._map_tracks.subject = self.song._song
        self._map_tracks()

    @subject_slot("tracks")
    def _map_tracks(self):
        # type: () -> Optional[SimpleTrack]
        self.parent.log_info("SongManager : mapping tracks")
        if len(self.song.tracks) and len(self.song._song.tracks) > len(self.song.tracks):
            self.song.tracks_added = True
        self.song.tracks = []
        for i, track in enumerate(list(self.song._song.tracks)):
            simple_track = SimpleTrack(track=track, index=i)
            self._live_track_to_simple_track[track] = simple_track
            self.song.tracks.append(simple_track)
        # link sub_tracks
        for track in self.song.tracks:
            if track._track.group_track:
                track.group_track = self._get_simple_track(track._track.group_track)
                track.group_track.sub_tracks.append(track)
                track.group_tracks = [track.group_track] + track.group_track.group_tracks
        # generate externalSynth tracks
        self.song.external_synth_tracks = [ExternalSynthTrack(track=track, index=track.index) for track in self.song.tracks if
                                           track.name in EXTERNAL_SYNTH_NAMES]
        self._simple_track_to_external_synth_track = {}
        for es_track in self.song.external_synth_tracks:
            self._simple_track_to_external_synth_track.update(
                {es_track.base_track: es_track, es_track.midi: es_track, es_track.audio: es_track})

        self._set_current_track()
        self.parent.log_info("SongManager : mapped tracks")

    def _get_simple_track(self, track, default=None):
        # type: (Any, Optional[SimpleTrack]) -> Optional[SimpleTrack]
        """ default is useful when the _ableton_track_to_simple_track is not built yet """
        if not track:
            return None
        if isinstance(track, AbstractTrack):
            raise Exception("Expected Live track, got AbstractTrack instead")

        if track not in self._live_track_to_simple_track.keys():
            if default:
                return default
            raise Exception("this track cannot be matched")

        return self._live_track_to_simple_track[track]

    def _set_current_track(self):
        self.song.selected_track = self._get_simple_track(self.song._view.selected_track)
        if self.song.selected_track in self._simple_track_to_external_synth_track:
            self.song.current_track = self._simple_track_to_external_synth_track[self.song.selected_track]
        else:
            self.song.current_track = self.song.selected_track

    def on_selected_track_changed(self):
        self._set_current_track()
