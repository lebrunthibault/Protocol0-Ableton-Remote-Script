from functools import partial

import Live
from typing import Optional

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import EXTERNAL_SYNTH_NAMES
from a_protocol_0.lom.track.TrackName import TrackName
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.lom.track.simple_track.SimpleGroupTrack import SimpleGroupTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer, subject_slot


class TrackManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(TrackManager, self).__init__(*a, **k)
        self.tracks_added = False
        self.automation_track_color = None
        self._added_track_listener.subject = self.parent.songManager

    @subject_slot("added_track")
    def _added_track_listener(self):
        self.parent.defer(self.song.current_track._added_track_init)

    def group_track(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(self.parent.clyphxNavigationManager.focus_main)
        seq.add(self.parent.keyboardShortcutManager.group_track, complete_on=self._added_track_listener)
        return seq.done()

    def create_midi_track(self, index, name=None):
        return self._create_track(track_creator=partial(self.song._song.create_midi_track, index), name=name)

    def create_audio_track(self, index, name=None):
        return self._create_track(track_creator=partial(self.song._song.create_audio_track, index), name=name)

    def _create_track(self, track_creator, name=None):
        # type: (callable, str) -> None
        self.parent.log_debug(name)
        seq = Sequence()
        seq.add(track_creator,
                complete_on=self.parent.trackManager._added_track_listener)

        @defer
        def set_name():
            TrackName(self.song.selected_track).name = name
            track_index = self.song.selected_track.index
            self.parent.songManager._tracks_listener()  # rebuild tracks
            # the underlying track object should have changed
            track = self.song.tracks[track_index]
            # track._added_track_init()  # manual call is needed
            # if track.group_track:
            #     track.group_track._added_track_init()  # the group track could change type as well

        if name is not None:
            seq.add(set_name)

        return seq.done()

    def instantiate_simple_track(self, track, index):
        # type: (Live.Track.Track, int) -> SimpleTrack
        if track.is_foldable:
            return SimpleGroupTrack(track=track, index=index)
        # elif AUTOMATION_TRACK_MIDI_NAME in track.name:
        #     return AutomationMidiTrack(track=track, index=index)
        # elif AUTOMATION_TRACK_AUDIO_NAME in track.name:
        #     return AutomationAudioTrack(track=track, index=index)
        else:
            return SimpleTrack(track=track, index=index)

    def instantiate_abstract_group_track(self, track):
        # type: (SimpleTrack) -> Optional[AbstractGroupTrack]
        if any([track.name in name for name in EXTERNAL_SYNTH_NAMES]):
            return ExternalSynthTrack(group_track=track)
        # if any([isinstance(sub_track, AutomationMidiTrack) for sub_track in track.sub_tracks]) and len(
        #         track.sub_tracks) == 2:
        #     wrapped_track = find_last(lambda t: t._track.has_audio_output, track.sub_tracks)
        #     if wrapped_track is None:
        #         raise RuntimeError("Tried to instantiate a WrappedTrack on a group with no audio output track")
        #     return WrappedTrack(group_track=track, wrapped_track=wrapped_track)

        return None
