import itertools
from functools import partial

from typing import TYPE_CHECKING, List

from _Framework.Util import forward_property
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.AutomationTracksCouple import AutomationTracksCouple
from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
from a_protocol_0.lom.track.simple_track.SimpleGroupTrack import SimpleGroupTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import throttle
from a_protocol_0.utils.log import log_ableton
from a_protocol_0.utils.utils import find_last

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class WrappedTrack(AbstractGroupTrack):
    def __init__(self, group_track, automation_tracks_couples, wrapped_track, *a, **k):
        # type: (SimpleTrack, List[AutomationTracksCouple], SimpleTrack) -> None
        self.wrapped_track = wrapped_track
        super(WrappedTrack, self).__init__(group_track=group_track, *a, **k)
        self.wrapped_track.track_name.link_track(self)
        self.automation_tracks_couples = automation_tracks_couples
        self._added_track_init()  # we need to call this here because the wrapped track instantiation doesn't happen at the same time as subtrack creation

    @staticmethod
    def make(group_track):
        # type: (SimpleGroupTrack) -> None
        automation_audio_tracks = [track for track in group_track.sub_tracks if isinstance(track, AutomationAudioTrack)]
        automation_midi_tracks = [track for track in group_track.sub_tracks if isinstance(track, AutomationMidiTrack)]
        if len(automation_audio_tracks) == 0 and len(automation_midi_tracks) == 0:
            return None
        main_tracks = [t for t in group_track.sub_tracks if t not in automation_audio_tracks + automation_midi_tracks]

        if len(main_tracks) != 1:
            raise Protocol0Error("a WrappedTrack should wrap one and only one main track")
        main_track = main_tracks[0]
        if main_track != group_track.sub_tracks[-1]:
            raise Protocol0Error("The main track of a Wrapped track should always be the last of the group")

        if len(automation_audio_tracks) != len(automation_midi_tracks):
            return None  # inconsistent state, happens on creation or when tracks are deleted

        # at this point we should have a consistent state with audio - midi * n and main track at this end
        # any other state is a bug and raises in AutomationTracksCouple __init__
        automation_tracks_couples = [AutomationTracksCouple(audio_track, midi_track) for audio_track, midi_track in itertools.izip(automation_audio_tracks, automation_midi_tracks)]

        return WrappedTrack(group_track=group_track, automation_tracks_couples=automation_tracks_couples, wrapped_track=main_tracks[0])

    def _added_track_init(self):
        seq = Sequence()
        seq.add(wait=1)
        seq.add(partial(self.wrapped_track.attach_output_routing_to, find_last(lambda t: isinstance(t, AutomationAudioTrack), self.sub_tracks)))
        seq.add(lambda: setattr(self, "name", self.wrapped_track.name))

        return seq.done()

    @property
    def name(self):
        # type: () -> str
        return self.base_track.name

    @name.setter
    # @throttle()
    def name(self, name):
        # type: (str) -> None
        self.parent.log_debug("setting name in wrapped track: %s" % name)
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
