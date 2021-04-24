from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.utils.utils import scroll_values


class AutomationTrackManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """

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
