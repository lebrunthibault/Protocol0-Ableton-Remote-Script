from functools import partial

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.AbstractAutomationTrack import AbstractAutomationTrack
from a_protocol_0.lom.track.simple_track.SimpleGroupTrack import SimpleGroupTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer


class AutomationTrackManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """

    @defer
    def create_automation_group(self, parameter):
        # type: (DeviceParameter) -> None
        """ first step, instrument track is selected """
        seq = Sequence()
        self.parent.songManager.abstract_group_track_creation_in_progress = True

        if self.song.current_track != self.song.selected_track:
            group_track = self.song.current_track
        elif self.song.selected_track.group_track:
            group_track = self.song.selected_track.group_track
        else:
            group_track = self.song.selected_track

        if not group_track.is_foldable or (isinstance(group_track, SimpleGroupTrack) and len(group_track.sub_tracks) > 1):
            seq.add(self.parent.trackManager.group_track)
        else:
            seq.add(lambda: setattr(self.song.current_track, "is_folded", False))

        track_name = AbstractAutomationTrack.get_automation_track_name_from_parameter(parameter)

        # this cannot be parallelized
        seq.add(partial(self.parent.trackManager.create_audio_track, group_track.index + 1, name=track_name))
        seq.add(partial(self.parent.trackManager.create_midi_track, group_track.index + 2, name=track_name))
        seq.add(lambda: setattr(self.parent.songManager, "abstract_group_track_creation_in_progress", False))
        seq.add(wait=1)
        seq.add(self.parent.songManager._tracks_listener)

        return seq.done()
