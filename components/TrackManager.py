from functools import partial

from typing import Optional

import Live

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_NAME, EXTERNAL_SYNTH_NAMES
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.lom.track.group_track.WrappedTrack import WrappedTrack
from a_protocol_0.lom.track.simple_track.AutomationTrack import AutomationTrack
from a_protocol_0.lom.track.simple_track.SimpleGroupTrack import SimpleGroupTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.utils.Sequence import Sequence
from a_protocol_0.utils.decorators import defer, subject_slot
from a_protocol_0.utils.utils import find_last


class TrackManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(TrackManager, self).__init__(*a, **k)
        self.tracks_added = False
        self.automation_track_color = None
        self._added_track_listener.subject = self.parent.songManager

    @subject_slot("added_track")
    def _added_track_listener(self):
        self.parent.defer(self.song.current_track._added_track_init)

    def group_track(self, seq=None):
        # type: (Sequence) -> None
        self.parent.keyboardShortcutManager.group_track()
        if seq:
            seq.add(complete_on=self._added_track_listener)

    def create_midi_track(self, index, name=None):
        # type: (int, str) -> None
        seq = Sequence()
        seq.add(partial(self.song._song.create_midi_track, index), complete_on=self.parent.trackManager._added_track_listener)

        @defer
        def set_name():
            TrackName(self.song.selected_track).name = name
            track_index = self.song.selected_track.index
            self.parent.songManager._tracks_listener()  # rebuild tracks
            # the underlying track object should have changed
            track = self.song.tracks[track_index]
            track._added_track_init()  # manual call is needed
            if track.group_track:
                track.group_track._added_track_init()  # the group track could change type as well

        if name is not None:
            seq.add(set_name)

        return seq

    def instantiate_simple_track(self, track, index):
        # type: (Live.Track.Track, int) -> SimpleTrack
        if track.is_foldable:
            return SimpleGroupTrack(track=track, index=index)
        elif AUTOMATION_TRACK_NAME in track.name and track.has_midi_input:
            return AutomationTrack(track=track, index=index)
        else:
            return SimpleTrack(track=track, index=index)

    def instantiate_abstract_group_track(self, track):
        # type: (SimpleTrack) -> Optional[AbstractGroupTrack]
        if any([track.name in name for name in EXTERNAL_SYNTH_NAMES]):
            return ExternalSynthTrack(group_track=track)
        if any([isinstance(sub_track, AutomationTrack) for sub_track in track.sub_tracks]) and len(track.sub_tracks) == 2:
            wrapped_track = find_last(lambda t: t._track.has_audio_output, track.sub_tracks)
            if wrapped_track is None:
                raise "Tried to instantiate a WrappedTrack on a group with no audio output track"
            return WrappedTrack(group_track=track, wrapped_track=wrapped_track)

        return None

