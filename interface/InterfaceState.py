from a_protocol_0.enums.TrackCategoryEnum import TrackCategoryEnum
from a_protocol_0.utils.utils import scroll_values


class InterfaceState(object):
    SELECTED_TRACK_CATEGORY = TrackCategoryEnum.ALL

    RECORDING_TIMES = [1, 2, 4, 8, 16, 32, 64]
    SELECTED_RECORDING_TIME = 4
    PROTECTED_MODE_ACTIVE = True  # protected mode prevents certain actions to be made

    # NB: for an unknown reason clip.view.show_envelope does not always show the envelope
    # when the button was not clicked. As a workaround we click it the first time
    CLIP_ENVELOPE_SHOW_BOX_CLICKED = False

    @classmethod
    def toggle_protected_mode(cls):
        # type: () -> None
        cls.PROTECTED_MODE_ACTIVE = not cls.PROTECTED_MODE_ACTIVE

    @classmethod
    def scroll_track_categories(cls, go_next):
        # type: (bool) -> None
        InterfaceState.SELECTED_TRACK_CATEGORY = scroll_values(
            list(TrackCategoryEnum), InterfaceState.SELECTED_TRACK_CATEGORY, go_next, True
        )

    @classmethod
    def scroll_recording_times(cls, go_next):
        # type: (bool) -> None
        cls.SELECTED_RECORDING_TIME = scroll_values(cls.RECORDING_TIMES, cls.SELECTED_RECORDING_TIME, go_next)
        bar_display_count = "%s bar%s" % (cls.SELECTED_RECORDING_TIME, "s" if cls.SELECTED_RECORDING_TIME > 1 else "")
        from a_protocol_0 import Protocol0

        Protocol0.SELF.show_message("Selected %s" % bar_display_count)
