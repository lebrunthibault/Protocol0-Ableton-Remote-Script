from typing import TYPE_CHECKING

from _Framework.Util import forward_property, find_if
from a_protocol_0.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class WrappedTrack(AbstractGroupTrack):
    def __init__(self, group_track, wrapped_track, *a, **k):
        # type: (SimpleTrack, SimpleTrack) -> None
        self.wrapped_track = wrapped_track
        self.wrapped_track.track_name.track = self
        super(WrappedTrack, self).__init__(group_track=group_track, *a, **k)

    def _added_track_init(self):
        self.base_track.output_routing_type = find_if(
            lambda r: r.attached_object == self.wrapped_track.output_routing_type.attached_object,
            self.base_track.available_output_routing_types)
        self.wrapped_track.output_routing_type = find_if(lambda r: r.display_name == self.base_track._track.name,
                                                         self.wrapped_track.available_output_routing_types)

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
