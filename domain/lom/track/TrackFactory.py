from typing import Optional, Type

import Live
from protocol0.domain.lom.instrument.instrument.InstrumentMinitaur import InstrumentMinitaur
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.AccessContainer import AccessContainer
from protocol0.shared.AccessSong import AccessSong


class TrackFactory(AccessContainer, AccessSong):
    def on_added_track(self):
        # type: () -> Optional[Sequence]
        if not self._song.selected_track.IS_ACTIVE:
            return None
        self._song.begin_undo_step()  # Live crashes on undo without this
        seq = Sequence()
        added_track = self._song.selected_track
        if self._song.selected_track == self._song.current_track.base_track:
            added_track = self._song.current_track
        seq.add(wait=1)
        seq.add(added_track._added_track_init)
        seq.add(self.container.song_scenes_manager.delete_empty_scenes)
        seq.add(self._song.end_undo_step)
        return seq.done()

    def instantiate_simple_track(self, track, index, cls):
        # type: (Live.Track.Track, int, Optional[Type[SimpleTrack]]) -> SimpleTrack
        # checking first on existing tracks
        existing_simple_track = self.container.song_tracks_manager.get_optional_simple_track(track)
        if existing_simple_track and (cls is None or isinstance(existing_simple_track, cls)):
            return existing_simple_track

        if cls is None:
            if track.name == SimpleInstrumentBusTrack.DEFAULT_NAME:
                cls = SimpleInstrumentBusTrack
            elif track.has_midi_input:
                cls = SimpleMidiTrack
            elif track.has_audio_input:
                cls = SimpleAudioTrack
            else:
                raise Protocol0Error("Unknown track type")

        return cls(
            track=track,
            index=index,
            song_tracks_manager=self.container.song_tracks_manager,
            device_manager=self.container.device_manager,
            browser_manager=self.container.browser_manager,
            click_manager=self.container.click_manager
        )

    def instantiate_abstract_group_track(self, base_group_track):
        # type: (SimpleTrack) -> AbstractGroupTrack
        if self._is_valid_external_synth_track(base_group_track):
            return self._make_external_synth_track(base_group_track=base_group_track)

        # handling normal group track
        previous_abstract_group_track = base_group_track.abstract_group_track

        if isinstance(previous_abstract_group_track, NormalGroupTrack):
            return previous_abstract_group_track
        else:
            return NormalGroupTrack(base_group_track=base_group_track, song_tracks_manager=self.container.song_tracks_manager)

    def _make_external_synth_track(self, base_group_track):
        # type: (SimpleTrack) -> ExternalSynthTrack
        """ discarding automated tracks in creation / suppression """
        midi_track = base_group_track.sub_tracks[0]

        if not midi_track.instrument:
            midi_track.instrument = InstrumentMinitaur(track=midi_track, device=None)

        if isinstance(base_group_track.abstract_group_track, ExternalSynthTrack):
            return base_group_track.abstract_group_track
        else:
            return ExternalSynthTrack(
                base_group_track=base_group_track,
                song_tracks_manager=self.container.song_tracks_manager
            )

    def _is_valid_external_synth_track(self, base_group_track):
        # type: (SimpleTrack) -> bool
        if len(base_group_track.sub_tracks) < 2:
            return False

        if not isinstance(base_group_track.sub_tracks[0], SimpleMidiTrack):
            return False
        if not isinstance(base_group_track.sub_tracks[1], SimpleAudioTrack):
            return False

        for track in base_group_track.sub_tracks[2:]:
            if not isinstance(track, SimpleAudioTrack):
                return False

        return True
