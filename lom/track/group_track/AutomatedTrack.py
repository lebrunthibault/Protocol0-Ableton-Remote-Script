from _Framework.Util import forward_property
from typing import TYPE_CHECKING, List

from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from a_protocol_0.lom.track.group_track.AutomationTracksCouple import AutomationTracksCouple

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AutomatedTrack(AbstractGroupTrack):
    def __init__(self, group_track, automation_tracks_couples, wrapped_track, *a, **k):
        # type: (SimpleTrack, List[AutomationTracksCouple], AbstractTrack) -> None
        super(AutomatedTrack, self).__init__(group_track=group_track, *a, **k)
        self.wrapped_track = wrapped_track
        self.instrument_track = self.wrapped_track.instrument_track
        self.wrapped_track.track_name.link_track(self)
        self.automation_tracks_couples = automation_tracks_couples
        self.link_audio_tracks()
        self._instrument_listener.subject = self.instrument_track
        self._instrument_listener()

        # linking sub tracks to self
        for automation_tracks_couple in automation_tracks_couples:
            automation_tracks_couple.audio_track.abstract_group_track = self
            automation_tracks_couple.midi_track.abstract_group_track = self

            if automation_tracks_couple.audio_track.index in self.parent.automationTrackManager.created_tracks_indexes:
                automation_tracks_couple.midi_track._added_track_init()

        self.wrapped_track.abstract_group_track = self

    def link_audio_tracks(self):
        audio_tracks = [self.base_track] + [couple.audio_track for couple in self.automation_tracks_couples] + [self.wrapped_track]
        for i, audio_track in enumerate(audio_tracks):
            if i == len(audio_tracks) - 1:
                break
            audio_tracks[i + 1].next_automated_audio_track = audio_track
            audio_track.previous_automated_audio_track = audio_tracks[i + 1]
            audio_tracks[i + 1].set_output_routing_to(audio_track)

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
        self.wrapped_track.action_arm_track()

    @forward_property('wrapped_track')
    def action_unarm_track(self): pass

    @forward_property('wrapped_track')
    def action_switch_monitoring(self): pass

    @forward_property('wrapped_track')
    def action_restart_and_record(self, *a, **k): pass

    @forward_property('wrapped_track')
    def action_record_all(self): pass

    @forward_property('wrapped_track')
    def action_record_audio_only(self, *a, **k): pass

    @forward_property('wrapped_track')
    def _post_record(self, *a, **k): pass

    @forward_property('wrapped_track')
    def action_undo_track(self): pass

    def disconnect(self):
        super(AutomatedTrack, self).disconnect()
        [automation_tracks_couple.disconnect() for automation_tracks_couple in self.automation_tracks_couples]
