from protocol0.enums.TrackCategoryEnum import TrackCategoryEnum
from protocol0.utils.utils import scroll_values


class InterfaceState(object):
    SELECTED_TRACK_CATEGORY = TrackCategoryEnum.ALL

    _RECORDING_BAR_LENGTHS = [1, 2, 4, 8, 16, 32, 64]
    SELECTED_RECORDING_BAR_LENGTH = 4

    # used only for partial scene duplication
    _DUPLICATE_BAR_LENGTHS = [-8, -4, -2, -1, 0, 1, 2, 4, 8]
    SELECTED_DUPLICATE_BAR_LENGTH = 0

    PROTECTED_MODE_ACTIVE = True  # protected mode prevents certain actions to be made

    # NB: for an unknown reason clip.view.show_envelope does not always show the envelope
    # when the button was not clicked. As a workaround we click it the first time
    CLIP_ENVELOPE_SHOW_BOX_CLICKED = False

    @classmethod
    def toggle_protected_mode(cls):
        # type: () -> None
        cls.PROTECTED_MODE_ACTIVE = not cls.PROTECTED_MODE_ACTIVE
        from protocol0 import Protocol0

        Protocol0.SELF.show_message("Protected mode %s" % ("on" if cls.PROTECTED_MODE_ACTIVE else "off"))

    @classmethod
    def scroll_track_categories(cls, go_next):
        # type: (bool) -> None
        InterfaceState.SELECTED_TRACK_CATEGORY = scroll_values(
            list(TrackCategoryEnum), InterfaceState.SELECTED_TRACK_CATEGORY, go_next, True
        )

    @classmethod
    def scroll_recording_bar_lengths(cls, go_next):
        # type: (bool) -> None
        cls.SELECTED_RECORDING_BAR_LENGTH = scroll_values(
            cls._RECORDING_BAR_LENGTHS, cls.SELECTED_RECORDING_BAR_LENGTH, go_next
        )
        cls._show_selected_bar_length(cls.SELECTED_RECORDING_BAR_LENGTH)

    @classmethod
    def scroll_duplicate_bar_lengths(cls, go_next):
        # type: (bool) -> None
        cls.SELECTED_DUPLICATE_BAR_LENGTH = scroll_values(
            cls._DUPLICATE_BAR_LENGTHS, cls.SELECTED_DUPLICATE_BAR_LENGTH, go_next
        )
        cls._show_selected_bar_length(cls.SELECTED_DUPLICATE_BAR_LENGTH)

    @classmethod
    def _show_selected_bar_length(cls, bar_length):
        # type: (int) -> None
        bar_display_count = "%s bar%s" % (bar_length, "s" if abs(bar_length) != 1 else "")
        from protocol0 import Protocol0

        Protocol0.SELF.show_message("Selected %s" % bar_display_count)
