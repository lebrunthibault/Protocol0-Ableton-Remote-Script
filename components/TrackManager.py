from typing import Optional, Any, Type

import Live
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.devices.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.devices.InstrumentMinitaur import InstrumentMinitaur
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.lom.track.group_track.SimpleGroupTrack import SimpleGroupTrack
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import p0_subject_slot, defer
from protocol0.utils.utils import find_if


class TrackManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackManager, self).__init__(*a, **k)
        self._added_track_listener.subject = self.parent.songManager

    @p0_subject_slot("added_track")
    @defer
    def _added_track_listener(self):
        # type: () -> Optional[Sequence]
        if not self.song.selected_track.is_active:
            return None
        self.song.begin_undo_step()  # Live crashes on undo without this
        seq = Sequence()
        added_track = self.song.selected_track
        if self.song.selected_track == self.song.current_track.base_track:
            added_track = self.song.current_track
        seq.add(added_track._added_track_init)
        seq.add(self.song.end_undo_step)
        return seq.done()

    def instantiate_simple_track(self, track, cls=None):
        # type: (Live.Track.Track, Optional[Type[SimpleTrack]]) -> SimpleTrack
        # checking first on existing tracks
        if track in self.song.live_track_to_simple_track:
            simple_track = self.song.live_track_to_simple_track[track]
            if cls is None or isinstance(simple_track, cls):
                return simple_track

        if cls is None:
            if track.name == SimpleInstrumentBusTrack.DEFAULT_NAME:
                cls = SimpleInstrumentBusTrack
            elif track.has_midi_input:
                cls = SimpleMidiTrack
            elif track.has_audio_input:
                cls = SimpleAudioTrack
            else:
                raise Protocol0Error("Unknown track type")

        return cls(track=track)

    def instantiate_abstract_group_track(self, base_group_track):
        # type: (SimpleTrack) -> AbstractGroupTrack
        previous_abstract_group_track = base_group_track.abstract_group_track

        ext_synth_track = self._make_external_synth_track(base_group_track=base_group_track)

        if ext_synth_track:
            abstract_group_track = ext_synth_track
        else:
            if isinstance(previous_abstract_group_track, ExternalSynthTrack):
                self.parent.log_error("An ExternalSynthTrack is changed to a SimpleGroupTrack")
            if isinstance(previous_abstract_group_track, SimpleGroupTrack):
                abstract_group_track = previous_abstract_group_track
            else:
                abstract_group_track = SimpleGroupTrack(base_group_track=base_group_track)

        abstract_group_track.post_init()

        return abstract_group_track

    def _make_external_synth_track(self, base_group_track):
        # type: (SimpleTrack) -> Optional[ExternalSynthTrack]
        """ discarding automated tracks in creation / suppression """
        if len(base_group_track.sub_tracks) < 2:
            return None

        midi_track = base_group_track.sub_tracks[0]
        audio_track = base_group_track.sub_tracks[1]
        if not isinstance(midi_track, SimpleMidiTrack) or not isinstance(audio_track, SimpleAudioTrack):
            return None

        if midi_track.name != SimpleMidiTrack.DEFAULT_NAME or audio_track.name != SimpleAudioTrack.DEFAULT_NAME:
            return None

        if any(isinstance(dummy_track, SimpleMidiTrack) for dummy_track in base_group_track.sub_tracks[2:]):
            return None

        instrument = find_if(lambda i: isinstance(i, AbstractExternalSynthTrackInstrument), [midi_track.instrument,
                                                                                             audio_track.instrument])  # type: Optional[AbstractExternalSynthTrackInstrument]
        if not instrument:
            midi_track.instrument = InstrumentMinitaur(track=midi_track, device=None)

        if isinstance(base_group_track.abstract_group_track, ExternalSynthTrack):
            # no track structure change, we can reuse the track
            return base_group_track.abstract_group_track
        else:
            return ExternalSynthTrack(base_group_track=base_group_track)

    def duplicate_current_track(self):
        # type: () -> Sequence
        return self.song.duplicate_track(self.song.current_track.index)

    def scroll_all_tracks_volume(self, go_next):
        # type: (bool) -> None
        for track in self.song.abstract_tracks:
            if isinstance(track, SimpleGroupTrack):
                continue
            track.scroll_volume(go_next=go_next)
