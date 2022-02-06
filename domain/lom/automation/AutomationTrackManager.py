from protocol0.application.interface.ClickManager import ClickManager
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.shared.utils import scroll_values
from protocol0.shared.AccessSong import AccessSong


class AutomationTrackManager(AccessSong):
    def __init__(self, click_manager):
        # type: (ClickManager) -> None
        self.click_manager = click_manager

    def display_selected_parameter_automation(self, clip, show_warning=True):
        # type: (Clip, bool) -> None
        selected_parameter = self.song.selected_parameter or clip.displayed_automated_parameter
        if selected_parameter is None:
            if len(clip.automated_parameters):
                selected_parameter = clip.automated_parameters[0]
            else:
                if show_warning:
                    raise Protocol0Warning("Selected clip has no automation")
                return None

        self.song.re_enable_automation()
        self.click_manager.show_clip_envelope_parameter(clip, selected_parameter)

    def scroll_automation_envelopes(self, go_next):
        # type: (bool) -> None
        selected_clip = self.song.selected_clip
        if not selected_clip:
            raise Protocol0Warning("No playable clip")

        automated_parameters = selected_clip.automated_parameters
        if len(automated_parameters) == 0:
            raise Protocol0Warning("No automated parameters")

        if selected_clip.displayed_automated_parameter is None:
            selected_clip.displayed_automated_parameter = automated_parameters[0]
        else:
            selected_clip.displayed_automated_parameter = scroll_values(
                automated_parameters, selected_clip.displayed_automated_parameter, go_next
            )

        self.display_selected_parameter_automation(selected_clip)
