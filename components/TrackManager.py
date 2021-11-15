from typing import Optional, Any

import Live
from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.devices.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.lom.track.group_track.SimpleGroupTrack import SimpleGroupTrack
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
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
        if not self.song.selected_track.is_active or isinstance(self.song.current_track, SimpleGroupTrack):
            return None
        self.song.begin_undo_step()  # Live crashes on undo without this
        seq = Sequence()
        seq.add(self.song.current_track._added_track_init)
        seq.add(self.song.end_undo_step)
        return seq.done()

    def instantiate_simple_track(self, track):
        # type: (Live.Track.Track) -> SimpleTrack
        # checking first on existing tracks
        if track in self.song.live_track_to_simple_track:
            simple_track = self.song.live_track_to_simple_track[track]
            simple_track.map_clip_slots()
        elif track.has_midi_input:
            simple_track = SimpleMidiTrack(track=track)
        elif track.has_audio_input:
            simple_track = SimpleAudioTrack(track=track)
        else:
            raise Protocol0Error("Unknown track type")

        # rebuild sub_tracks
        simple_track.sub_tracks = []
        simple_track.link_group_track()

        return simple_track

    def instantiate_abstract_group_track(self, base_group_track):
        # type: (SimpleTrack) -> AbstractGroupTrack
        if not base_group_track.is_foldable:
            raise Protocol0Error(
                "You passed a non group_track to instantiate_abstract_group_track : %s" % base_group_track
            )

        previous_abstract_group_track = base_group_track.abstract_group_track

        abstract_group_track = self.make_external_synth_track(base_group_track=base_group_track)
        if not abstract_group_track:
            if isinstance(previous_abstract_group_track, SimpleGroupTrack):
                abstract_group_track = previous_abstract_group_track
            else:
                abstract_group_track = SimpleGroupTrack(base_group_track=base_group_track)

        if self.song.is_loading and abstract_group_track.is_armed:
            abstract_group_track.has_monitor_in = False
        return abstract_group_track

    def make_external_synth_track(self, base_group_track):
        # type: (SimpleTrack) -> Optional[ExternalSynthTrack]
        """ discarding automated tracks in creation / suppression """
        midi_track = base_group_track.sub_tracks[0]
        audio_track = base_group_track.sub_tracks[1]
        if not isinstance(midi_track, SimpleMidiTrack) or not isinstance(audio_track, SimpleAudioTrack):
            return None

        instrument = find_if(lambda i: isinstance(i, AbstractExternalSynthTrackInstrument), [midi_track.instrument, audio_track.instrument])  # type: Optional[AbstractExternalSynthTrackInstrument]
        if not instrument:
            self.parent.log_error("Couldn't find external instrument in %s" % base_group_track)
            return None

        if isinstance(base_group_track.abstract_group_track, ExternalSynthTrack) and len(base_group_track.abstract_group_track.sub_tracks) == len(base_group_track.sub_tracks):
            external_synth_track = base_group_track.abstract_group_track
            if len(external_synth_track.base_track.clip_slots) != len(base_group_track.clip_slots):
                external_synth_track.link_clip_slots()
        else:
            external_synth_track = ExternalSynthTrack(base_group_track=base_group_track)
            external_synth_track.link_parent_and_child_objects()

        return external_synth_track

    def duplicate_current_track(self):
        # type: () -> Sequence
        return self.song.duplicate_track(self.song.current_track.index)

    def scroll_all_tracks_volume(self, go_next):
        # type: (bool) -> None
        for track in self.song.abstract_tracks:
            if isinstance(track, SimpleGroupTrack):
                continue
            if track.top_group_track.base_name == "Drums":
                continue
            track.scroll_volume(go_next=go_next)
