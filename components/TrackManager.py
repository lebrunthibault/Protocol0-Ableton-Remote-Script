from functools import partial

import Live
from typing import Optional, Callable, Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.device.Device import Device
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.lom.track.group_track.SimpleGroupTrack import SimpleGroupTrack
from a_protocol_0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from a_protocol_0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot, defer


class TrackManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackManager, self).__init__(*a, **k)
        self._added_track_listener.subject = self.parent.songManager

    @p0_subject_slot("added_track")
    @defer
    def _added_track_listener(self):
        # type: () -> Sequence
        self.song.begin_undo_step()  # Live crashes on undo without this
        seq = Sequence()
        seq.add(self.song.current_track._added_track_init)
        seq.add(self.song.end_undo_step)
        return seq.done()

    def group_track(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(self.parent.clyphxNavigationManager.focus_main)
        seq.add(
            self.parent.keyboardShortcutManager.group_track,
            complete_on=self._added_track_listener,
            check_timeout=4,
        )
        return seq.done()

    def create_midi_track(self, index, name, device=None):
        # type: (int, str, Device) -> Sequence
        return self._create_track(
            track_creator=partial(self.song._song.create_midi_track, index), name=name, device=device
        )

    def create_audio_track(self, index, name, device=None):
        # type: (int, str, Device) -> Sequence
        return self._create_track(
            track_creator=partial(self.song._song.create_audio_track, index), name=name, device=device
        )

    def _create_track(self, track_creator, name, device):
        # type: (Callable, str, Optional[Device]) -> Sequence
        seq = Sequence().add(wait=1, silent=True)  # defer change
        seq.add(track_creator, complete_on=self.parent.songManager._tracks_listener)
        seq.add(
            lambda: self.song.selected_track.track_name.update(base_name=name),
            name="set track name to %s" % name,
        )
        if device:
            seq.add(lambda: self.song.selected_track.clear_devices(), name="clear devices")
            seq.add(
                partial(
                    self.parent.browserManager.load_any_device,
                    device_type=device.device_type,
                    device_name=device.name,
                ),
                silent=True,
            )

        return seq.done()

    def instantiate_simple_track(self, track, index):
        # type: (Live.Track.Track, int) -> SimpleTrack
        # checking first on existing tracks
        if track in self.parent.songManager.live_track_to_simple_track:
            simple_track = self.parent.songManager.live_track_to_simple_track[track]
            simple_track.map_clip_slots()
            return simple_track
        # if index == self.song.AUDIO_BUS_TRACK_INDEX:
        #     return AudioBusTrack(track=track, index=index)
        if track.has_midi_input:
            return SimpleMidiTrack(track=track, index=index)
        elif track.has_audio_input:
            return SimpleAudioTrack(track=track, index=index)

        assert False, "unknown track type %s" % track

    def instantiate_abstract_group_track(self, group_track):
        # type: (SimpleTrack) -> AbstractGroupTrack
        if not group_track.is_foldable:
            raise Protocol0Error("You passed a non group_track to instantiate_abstract_group_track : %s" % group_track)

        # calling factories by most specific first
        abstract_group_track = self.make_external_synth_track(group_track=group_track)
        if not abstract_group_track:
            abstract_group_track = SimpleGroupTrack(group_track=group_track)

        # this should be here because as abstract_group_track creation is conditional on sub_track state
        # we first check if the track could be created, then if it's the same type and return it if we have a match
        if group_track in self.parent.songManager.live_track_to_simple_track:
            previous_group_track = self.parent.songManager.live_track_to_simple_track[group_track]
            if type(abstract_group_track) is type(previous_group_track):
                abstract_group_track.disconnect()
                return previous_group_track

        return abstract_group_track

    def make_external_synth_track(self, group_track):
        # type: (SimpleTrack) -> Optional[ExternalSynthTrack]
        """ discarding automated tracks in creation / suppression """
        if len(group_track.sub_tracks) != 2:
            return None

        if not isinstance(group_track.sub_tracks[0], SimpleMidiTrack) or not isinstance(
            group_track.sub_tracks[1], SimpleAudioTrack
        ):
            return None

        is_external_synth_track = False
        if any(sub_track.instrument and sub_track.instrument.IS_EXTERNAL_SYNTH for sub_track in group_track.sub_tracks):
            is_external_synth_track = True
        # minitaur is a special case as it doesn't have a vst
        # elif group_track.track_name.base_name.lower() == InstrumentMinitaur.NAME:
        #     is_external_synth_track = True

        return ExternalSynthTrack(group_track=group_track) if is_external_synth_track else None
