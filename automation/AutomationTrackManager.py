from functools import partial

import deprecation
from typing import Set, Optional, Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.enums.DirectionEnum import DirectionEnum
from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.lom.clip.AutomationAudioClip import AutomationAudioClip
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.utils.decorators import defer
from a_protocol_0.utils.utils import scroll_values


class AutomationTrackManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AutomationTrackManager, self).__init__(*a, **k)
        self.current_parameter = None  # type: Optional[DeviceParameter]
        self.created_tracks_indexes = set()  # type: Set[int]

    def display_selected_parameter_automation(self):
        # type: () -> None
        if self.song.selected_parameter is None:
            self.parent.show_message("No selected parameter")
            return None
        if not self.song.selected_track.playable_clip:
            self.parent.show_message("No playable clip")
            return

        self.song.selected_track.playable_clip.show_envelope_parameter(self.song.selected_parameter)

    def scroll_automation_envelopes(self, go_next):
        # type: (bool) -> None
        playable_clip = self.song.selected_track.playable_clip
        if not playable_clip:
            self.parent.show_message("No playable clip")
            return
        automated_parameters = playable_clip.automated_parameters
        if len(automated_parameters) == 0:
            self.parent.show_message("No automated parameters")
            return
        if playable_clip.displayed_automated_parameter is None:
            playable_clip.displayed_automated_parameter = automated_parameters[0]
        else:
            playable_clip.displayed_automated_parameter = scroll_values(
                automated_parameters, playable_clip.displayed_automated_parameter, go_next
            )

        self.song.selected_track.playable_clip.show_envelope_parameter(playable_clip.displayed_automated_parameter)

    @deprecation.deprecated()
    @defer
    def create_automation_group(self):
        # type: () -> Optional[Sequence]
        """ create 2 automation dummy tracks for the selected parameter """
        if self.song.selected_parameter is None:
            self.parent.show_message("No selected parameter")
            return None

        # here we store this parameter so that the midi track can access it
        # before the audio track has loaded the device from the browser. Makes the track creation faster
        self.current_parameter = self.song.selected_parameter
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

        track_name = "_%s" % self.current_parameter.name

        # this should not be parallelized
        seq.add(
            partial(
                self.parent.trackManager.create_audio_track,
                base_track.index + 1,
                name=track_name,
                device=self.current_parameter.device,
            )
        )
        seq.add(partial(self.parent.trackManager.create_midi_track, base_track.index + 2, name=track_name))
        seq.add(
            partial(setattr, self.parent.songManager, "abstract_group_track_creation_in_progress", False),
            silent=False,
        )
        # storing the indexes makes the setup faster
        seq.add(
            partial(setattr, self, "created_tracks_indexes", set([base_track.index + 1, base_track.index + 2])),
            silent=True,
        )
        # instantiating AutomatedTrack on first parameter automation
        seq.add(self.parent.songManager._tracks_listener, name="AutomatedTrack creation")  # type: ignore[arg-type]
        seq.add(partial(setattr, self, "created_tracks_indexes", set()), silent=True)

        return seq.done()

    def adjust_clip_automation_curve(self, go_next=True, reset=False, direction=DirectionEnum.UP):
        # type: (bool, bool, DirectionEnum) -> None
        if not isinstance(self.song.selected_clip, AbstractAutomationClip):
            return None

        clip = self.song.selected_clip
        assert isinstance(clip, AbstractAutomationClip)
        if not isinstance(clip, AutomationAudioClip):
            assert isinstance(clip.linked_clip, AutomationAudioClip)
            clip = clip.linked_clip

        if reset:
            clip.automation_ramp_up.is_active = clip.automation_ramp_down.is_active = False
            return None

        if direction == DirectionEnum.UP:
            clip.automation_ramp_up.scroll(go_next=go_next)
        else:
            clip.automation_ramp_down.scroll(go_next=go_next)
