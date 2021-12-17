from typing import Optional, Any, Type

import Live
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.devices.InstrumentMinitaur import InstrumentMinitaur
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import p0_subject_slot


class TrackManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackManager, self).__init__(*a, **k)
        self._added_track_listener.subject = self.parent.songManager

    @p0_subject_slot("added_track")
    def _added_track_listener(self):
        # type: () -> Optional[Sequence]
        if not self.song.selected_track.IS_ACTIVE:
            return None
        self.song.begin_undo_step()  # Live crashes on undo without this
        seq = Sequence()
        added_track = self.song.selected_track
        if self.song.selected_track == self.song.current_track.base_track:
            added_track = self.song.current_track
        seq.add(added_track._added_track_init)
        seq.add(self.song.end_undo_step)
        return seq.done()

    def instantiate_simple_track(self, track, cls):
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
        # type: (SimpleTrack) -> None
        ext_synth_track = self._make_external_synth_track(base_group_track=base_group_track)
        previous_abstract_group_track = base_group_track.abstract_group_track

        if ext_synth_track:
            abstract_group_track = ext_synth_track
        else:
            if isinstance(previous_abstract_group_track, ExternalSynthTrack):
                self.parent.log_error("An ExternalSynthTrack is changed to a NormalGroupTrack")
            if isinstance(previous_abstract_group_track, NormalGroupTrack):
                abstract_group_track = previous_abstract_group_track
            else:
                abstract_group_track = NormalGroupTrack(base_group_track=base_group_track)

        if previous_abstract_group_track and previous_abstract_group_track != abstract_group_track:
            previous_abstract_group_track.disconnect()

        abstract_group_track.on_grid_change()

    def _make_external_synth_track(self, base_group_track):
        # type: (SimpleTrack) -> Optional[ExternalSynthTrack]
        """ discarding automated tracks in creation / suppression """
        if len(base_group_track.sub_tracks) < 2:
            return None

        midi_track = base_group_track.sub_tracks[0]
        audio_track = base_group_track.sub_tracks[1]
        if not isinstance(midi_track, SimpleMidiTrack) or not isinstance(audio_track, SimpleAudioTrack):
            return None

        for track in base_group_track.sub_tracks[2:]:
            if not isinstance(track, SimpleAudioTrack):
                return None

        if not midi_track.instrument:
            midi_track.instrument = InstrumentMinitaur(track=midi_track, device=None)

        if isinstance(base_group_track.abstract_group_track, ExternalSynthTrack) and all(
                not isinstance(sub_track, SimpleAudioTrack) for sub_track in base_group_track.sub_tracks[2:]):
            # no track structure change, we can reuse the track
            return base_group_track.abstract_group_track
        else:
            return ExternalSynthTrack(base_group_track=base_group_track)

    def append_to_sub_tracks(self, group_track, sub_track, previous_sub_track=None):
        # type: (AbstractTrack, AbstractTrack, Optional[AbstractTrack]) -> None
        if sub_track in group_track.sub_tracks:
            return

        if previous_sub_track is None or previous_sub_track not in group_track.sub_tracks:
            group_track.sub_tracks.append(sub_track)
        else:
            sub_track_index = group_track.sub_tracks.index(previous_sub_track)
            group_track.sub_tracks[sub_track_index] = sub_track
