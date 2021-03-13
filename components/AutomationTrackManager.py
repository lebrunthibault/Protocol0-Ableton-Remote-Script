from functools import partial
from typing import Set

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.lom.track.simple_track.AbstractAutomationTrack import AbstractAutomationTrack
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer


class AutomationTrackManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """
    def __init__(self, *a, **k):
        super(AutomationTrackManager, self).__init__(*a, **k)
        self.current_parameter = None  # type: DeviceParameter
        self.created_tracks_indexes = set()  # type: Set[int]

    @defer
    def create_automation_group(self, parameter):
        # type: (DeviceParameter) -> None
        """ first step, instrument track is selected """
        if parameter is None:
            self.parent.show_message("No selected parameter")
            return

        # here we store this parameter so that the midi track can access it
        # before the audio track has loaded the device from the browser. Makes the track creation faster
        self.current_parameter = parameter
        seq = Sequence()
        self.parent.songManager.abstract_group_track_creation_in_progress = True

        if self.song.selected_track.abstract_group_track:
            base_track = self.song.selected_track.abstract_group_track
        elif self.song.selected_track.group_track and len(self.song.selected_track.group_track.sub_tracks) == 1:
            base_track = self.song.selected_track.group_track
        else:
            base_track = self.song.selected_track

        if not base_track.is_foldable:
            seq.add(self.parent.trackManager.group_track)
        else:
            seq.add(lambda: setattr(self.song.current_track, "is_folded", False), name="unfold group track")

        track_name = AbstractAutomationTrack.get_automation_track_name_from_parameter(parameter)

        # this should not be parallelized
        seq.add(partial(self.parent.trackManager.create_audio_track, base_track.index + 1, name=track_name, device=parameter.device))
        seq.add(partial(self.parent.trackManager.create_midi_track, base_track.index + 2, name=track_name))
        seq.add(lambda: setattr(self.parent.songManager, "abstract_group_track_creation_in_progress", False))
        # storing the indexes makes the setup faster
        seq.add(partial(setattr, self, "created_tracks_indexes", set([base_track.index + 1, base_track.index + 2])))
        seq.add(self.parent.songManager._tracks_listener)  # instantiating AutomatedTrack on first parameter automation
        seq.add(partial(setattr, self, "created_tracks_indexes", set()))

        return seq.done()
