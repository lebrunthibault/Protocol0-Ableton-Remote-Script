from functools import partial

import Live
from typing import Optional

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_NAME
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.lom.track.group_track.AutomatedTrack import AutomatedTrack
from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
from a_protocol_0.lom.track.simple_track.SimpleGroupTrack import SimpleGroupTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import subject_slot


class TrackManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(TrackManager, self).__init__(*a, **k)
        self.tracks_added = False
        self.automation_track_color = None
        self._added_track_listener.subject = self.parent.songManager

    @subject_slot("added_track")
    def _added_track_listener(self):
        seq = Sequence().add(wait=1).add(self.song.current_track._added_track_init)
        return seq.done()

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
        seq = Sequence()
        seq.add(wait=1)
        seq.add(track_creator, complete_on=self._added_track_listener)

        def set_name():
            seq = Sequence()
            seq.add(partial(self.song.selected_track.track_name.set, base_name=name))
            seq.add(self.parent.songManager._tracks_listener)  # rebuild tracks
            # the underlying track object should have changed
            track = self.song.tracks[self.song.selected_track.index]
            seq.add(wait=1)
            seq.add(track._added_track_init)  # manual call is needed, as _added_track_listener is not going to be called
            if track.abstract_group_track:
                seq.add(track.abstract_group_track._added_track_init)  # the group track could change type as well

            return seq.done()

        if name is not None:
            seq.add(wait=1)
            seq.add(set_name)

        return seq.done()

    def instantiate_simple_track(self, track, index):
        # type: (Live.Track.Track, int) -> SimpleTrack
        if track.is_foldable:
            return SimpleGroupTrack(track=track, index=index)
        elif AUTOMATION_TRACK_NAME in track.name:
            if track.has_midi_input:
                return AutomationMidiTrack(track=track, index=index)
            else:
                return AutomationAudioTrack(track=track, index=index)
        else:
            return SimpleTrack(track=track, index=index)

    def instantiate_abstract_group_track(self, track):
        # type: (SimpleGroupTrack) -> Optional[AbstractGroupTrack]
        external_synth_track = ExternalSynthTrack.make(group_track=track)
        if external_synth_track:
            return AutomatedTrack.make(group_track=external_synth_track) or external_synth_track

        wrapped_track = AutomatedTrack.make(group_track=track)
        if wrapped_track:
            return wrapped_track

        return None
