import itertools
from functools import partial

import Live
from typing import Optional

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import AUTOMATION_TRACK_NAME, EXTERNAL_SYNTH_NAMES
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.AutomatedTrack import AutomatedTrack
from a_protocol_0.lom.track.group_track.AutomationTracksCouple import AutomationTracksCouple
from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.lom.track.simple_track.AbstractAutomationTrack import AbstractAutomationTrack
from a_protocol_0.lom.track.simple_track.SimpleGroupTrack import SimpleGroupTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import p0_subject_slot


class TrackManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(TrackManager, self).__init__(*a, **k)
        self.tracks_added = False
        self.automation_track_color = None
        self._added_track_listener.subject = self.parent.songManager
        self._selected_track_listener.subject = self.parent.songManager

    @p0_subject_slot("added_track")
    def _added_track_listener(self):
        if not self.parent.songManager.abstract_group_track_creation_in_progress:
            seq = Sequence().add(wait=1).add(self.song.current_track._added_track_init)
            return seq.done()

    @p0_subject_slot("selected_track")
    def _selected_track_listener(self):
        self.parent.defer(self._update_nav_view)

    def _update_nav_view(self):
        if self.song.selected_track.nav_view == "clip":
            self.parent.clyphxNavigationManager.show_clip_view()
        elif self.song.selected_track.nav_view == "track":
            self.parent.clyphxNavigationManager.show_track_view()

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
            # easier to have this here instead of using lambda to get dynamic variables
            seq = Sequence()
            seq.add(partial(self.song.selected_track.track_name.set, base_name=name))
            seq.add(self.parent.songManager._tracks_listener)  # rebuild tracks
            # the underlying track object should have changed
            track = self.song.simple_tracks[self.song.selected_track.index]
            seq.add(wait=1)
            seq.add(track._added_track_init)  # manual call is needed, as _added_track_listener is not going to be called
            # if track.abstract_group_track:
            #     seq.add(track.abstract_group_track._added_track_init)  # the group track could change type as well

            return seq.done()

        if name is not None:
            seq.add(wait=1)
            seq.add(set_name)

        return seq.done()

    def instantiate_simple_track(self, track, index):
        # type: (Live.Track.Track, int) -> SimpleTrack
        if track.is_foldable:
            return SimpleGroupTrack(track=track, index=index)
        else:
            return SimpleTrack(track=track, index=index)

    def instantiate_abstract_group_track(self, group_track):
        # type: (SimpleGroupTrack) -> Optional[AbstractGroupTrack]
        external_synth_track = self.make_external_synth_track(group_track=group_track)
        if external_synth_track:
            return self.make_automated_track(group_track=group_track, wrapped_track=external_synth_track) or external_synth_track

        wrapped_track = self.make_automated_track(group_track=group_track)
        if wrapped_track:
            return wrapped_track

        return None

    def make_external_synth_track(self, group_track):
        # type: (SimpleGroupTrack) -> None
        if len([sub_track for sub_track in group_track.sub_tracks if not TrackManager._is_automated_sub_track(sub_track)]) != 2:
            return
        if not any([name.lower() in group_track.track_name.base_name.lower() for name in EXTERNAL_SYNTH_NAMES]):
            return

        return ExternalSynthTrack(group_track=group_track)

    def make_automated_track(self, group_track, wrapped_track=None):
        # type: (SimpleGroupTrack, AbstractGroupTrack) -> None
        try:
            return self._make_automated_track(group_track=group_track, wrapped_track=wrapped_track)
        except Protocol0Error as e:
            # don't raise when the tracks are created
            if self.parent.songManager.abstract_group_track_creation_in_progress:
                return None
            else:
                raise e

    def _make_automated_track(self, group_track, wrapped_track=None):
        # type: (SimpleGroupTrack, AbstractTrack) -> Optional[AutomatedTrack]
        automation_audio_tracks = [track for track in group_track.sub_tracks if TrackManager._is_automated_sub_track(track) and track.is_audio]
        automation_midi_tracks = [track for track in group_track.sub_tracks if TrackManager._is_automated_sub_track(track) and track.is_midi]

        if len(automation_audio_tracks) == 0 and len(automation_midi_tracks) == 0:
            return None
        main_tracks = [t for t in group_track.sub_tracks if t not in automation_audio_tracks + automation_midi_tracks]

        if wrapped_track is None:
            if len(main_tracks) != 1:
                # raise Protocol0Error("an AutomatedTrack should wrap one and only one main track (or one composite track)")
                return None
            wrapped_track = main_tracks[0]
            if wrapped_track != group_track.sub_tracks[-1]:
                raise Protocol0Error("The main track of a AutomatedTrack track should always be the last of the group")

        if len(automation_audio_tracks) != len(automation_midi_tracks):
            return None  # inconsistent state, happens on creation or when tracks are deleted

        # at this point we should have a consistent state with audio - midi * n and main track at this end
        # any other state is a bug and raises in AutomationTracksCouple __init__
        automation_tracks_couples = [AutomationTracksCouple(group_track, audio_track, midi_track) for audio_track, midi_track in itertools.izip(automation_audio_tracks, automation_midi_tracks)]

        return AutomatedTrack(group_track=group_track, automation_tracks_couples=automation_tracks_couples, wrapped_track=wrapped_track)

    @staticmethod
    def _is_automated_sub_track(track):
        # type: (SimpleTrack) -> bool
        return AUTOMATION_TRACK_NAME in track.name and AbstractAutomationTrack.get_parameter_info(track.name)