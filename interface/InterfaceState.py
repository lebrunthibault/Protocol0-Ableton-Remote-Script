from a_protocol_0.enums.TrackCategoryEnum import TrackCategoryEnum
from a_protocol_0.utils.utils import scroll_values


class InterfaceState(object):
    SELECTED_TRACK_CATEGORY = TrackCategoryEnum.ALL

    RECORDING_TIMES = [1, 2, 4, 8, 16, 32, 64]
    SELECTED_RECORDING_TIME = 1

    # NB: for an unknown reason clip.view.show_envelope does not always show the envelope
    # when the button was not clicked. As a workaround we click it the first time
    CLIP_ENVELOPE_SHOW_BOX_CLICKED = False

    def scroll_track_categories(self, go_next):
        # type: (bool) -> None
        InterfaceState.SELECTED_TRACK_CATEGORY = scroll_values(
            list(TrackCategoryEnum), InterfaceState.SELECTED_TRACK_CATEGORY, go_next, True
        )

    def scroll_recording_times(self, go_next):
        # type: (bool) -> None
        self.SELECTED_RECORDING_TIME = scroll_values(self.RECORDING_TIMES, self.SELECTED_RECORDING_TIME, go_next)
        bar_display_count = "%s bar%s" % (self.SELECTED_RECORDING_TIME, "s" if self.SELECTED_RECORDING_TIME > 1 else "")
        from a_protocol_0 import Protocol0

        Protocol0.SELF.show_message("Selected %s" % bar_display_count)
