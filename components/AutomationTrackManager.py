from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.errors.Protocol0Warning import Protocol0Warning
from protocol0.utils.utils import scroll_values


class AutomationTrackManager(AbstractControlSurfaceComponent):
    """ Handles the creation, grouping and routing of an automation track """

    def display_selected_parameter_automation(self):
        # type: () -> None
        if not self.song.selected_clip:
            raise Protocol0Warning("No clip selected")

        selected_parameter = self.song.selected_parameter or self.song.selected_clip.displayed_automated_parameter
        if selected_parameter is None:
            if len(self.song.selected_clip.automated_parameters):
                selected_parameter = self.song.selected_clip.automated_parameters[0]
            else:
                raise Protocol0Warning("Selected clip has no automation")

        self.song.re_enable_automation()
        self.parent.uiManager.show_clip_envelope_parameter(self.song.selected_clip, selected_parameter)

    def scroll_automation_envelopes(self, go_next):
        # type: (bool) -> None
        selected_clip = self.song.selected_clip
        if not selected_clip:
            self.parent.show_message("No playable clip")
            return
        automated_parameters = selected_clip.automated_parameters
        if len(automated_parameters) == 0:
            self.parent.show_message("No automated parameters")
            return
        if selected_clip.displayed_automated_parameter is None:
            selected_clip.displayed_automated_parameter = automated_parameters[0]
        else:
            selected_clip.displayed_automated_parameter = scroll_values(
                automated_parameters, selected_clip.displayed_automated_parameter, go_next
            )

        self.display_selected_parameter_automation()
