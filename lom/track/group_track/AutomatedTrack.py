import itertools

from typing import TYPE_CHECKING, List, Union

from _Framework.Util import forward_property
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.AutomationTracksCouple import AutomationTracksCouple
from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
from a_protocol_0.lom.track.simple_track.SimpleGroupTrack import SimpleGroupTrack
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AutomatedTrack(AbstractGroupTrack):
    def __init__(self, group_track, automation_tracks_couples, wrapped_track, *a, **k):
        # type: (SimpleTrack, List[AutomationTracksCouple], AbstractTrack) -> None
        self.wrapped_track = wrapped_track
        super(AutomatedTrack, self).__init__(group_track=group_track, *a, **k)
        self.wrapped_track.track_name.link_track(self)
        self.automation_tracks_couples = automation_tracks_couples
        self._added_track_init()  # we need to call this here because the wrapped track instantiation doesn't happen at the same time as subtrack creation

    @staticmethod
    def make(group_track):
        # type: (SimpleGroupTrack) -> None
        try:
            return AutomatedTrack._make(group_track=group_track)
        except Protocol0Error as e:
            # don't raise when the tracks are created
            from a_protocol_0 import Protocol0
            if Protocol0.SELF.songManager.abstract_group_track_creation_in_progress:
                return None
            else:
                raise e

    @staticmethod
    def _make(group_track):
        # type: (Union[AbstractGroupTrack, SimpleGroupTrack]) -> None
        automation_audio_tracks = [track for track in group_track.sub_tracks if isinstance(track, AutomationAudioTrack)]
        automation_midi_tracks = [track for track in group_track.sub_tracks if isinstance(track, AutomationMidiTrack)]
        if len(automation_audio_tracks) == 0 and len(automation_midi_tracks) == 0:
            return None
        main_tracks = [t for t in group_track.sub_tracks if t not in automation_audio_tracks + automation_midi_tracks]

        if isinstance(group_track, AbstractGroupTrack):
            wrapped_track = group_track  # here we wrap and abstractGroupTrack, so the group track is gonna be composed twice
            # but we're going to handle only the AutomatedTrack directly
        else:
            if len(main_tracks) != 1:
                raise Protocol0Error("an AutomatedTrack should wrap one and only one main track (or one composite track)")
            wrapped_track = main_tracks[0]
            if wrapped_track != group_track.sub_tracks[-1]:
                raise Protocol0Error("The main track of a AutomatedTrack track should always be the last of the group")

        if len(automation_audio_tracks) != len(automation_midi_tracks):
            return None  # inconsistent state, happens on creation or when tracks are deleted

        # at this point we should have a consistent state with audio - midi * n and main track at this end
        # any other state is a bug and raises in AutomationTracksCouple __init__
        automation_tracks_couples = [AutomationTracksCouple(audio_track, midi_track) for audio_track, midi_track in itertools.izip(automation_audio_tracks, automation_midi_tracks)]

        return AutomatedTrack(group_track=group_track, automation_tracks_couples=automation_tracks_couples, wrapped_track=wrapped_track)

    def _added_track_init(self):
        seq = Sequence()
        seq.add(wait=1)
        seq.add(self.link_audio_tracks)
        seq.add(lambda: setattr(self, "name", self.wrapped_track.name))

        return seq.done()

    def link_audio_tracks(self):
        audio_tracks = [self.base_track] + [couple.audio_track for couple in self.automation_tracks_couples] + [self.wrapped_track]
        for i, audio_track in enumerate(audio_tracks):
            if i == len(audio_tracks) - 1:
                break
            audio_tracks[i + 1].attach_output_routing_to(audio_track)

    @property
    def name(self):
        # type: () -> str
        return self.base_track.name

    @name.setter
    def name(self, name):
        # type: (str) -> None
        self.base_track.name = name
        self.wrapped_track.name = name

    @forward_property('wrapped_track')
    def arm(): pass

    @forward_property('wrapped_track')
    def is_playing(): pass

    @forward_property('wrapped_track')
    def is_recording(): pass

    @forward_property('wrapped_track')
    def next_empty_clip_slot_index(): pass

    def action_arm_track(self):
        self.is_folded = False
        self.wrapped_track.arm = True
        self.wrapped_track.mute = False

    @forward_property('wrapped_track')
    def action_unarm_track(self): pass

    @forward_property('wrapped_track')
    def action_switch_monitoring(self): pass

    @forward_property('wrapped_track')
    def action_record_all(self): pass

    @forward_property('wrapped_track')
    def action_record_audio_only(self): pass

    @forward_property('wrapped_track')
    def action_undo_track(self): pass
