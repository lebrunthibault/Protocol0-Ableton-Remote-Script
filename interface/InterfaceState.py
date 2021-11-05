from protocol0.enums.RecordingTimeEnum import RecordingTimeEnum
from protocol0.my_types import StringOrNumber
from protocol0.utils.decorators import save_to_song_data, song_synchronizable_class
from protocol0.utils.utils import scroll_values


@song_synchronizable_class
class InterfaceState(object):
    SELECTED_RECORDING_TIME = RecordingTimeEnum.FOUR

    RECORD_CLIP_TAILS = False  # records one more bar of audio to make editing easier
    SELECTED_CLIP_TAILS_BAR_LENGTH = 1

    PROTECTED_MODE_ACTIVE = True  # protected mode prevents certain actions to be made

    # NB: for an unknown reason clip.view.show_envelope does not always show the envelope
    # when the button was not clicked. As a workaround we click it the first time
    CLIP_ENVELOPE_SHOW_BOX_CLICKED = False

    @classmethod
    def record_clip_tails_length(cls):
        # type: () -> int
        return cls.SELECTED_CLIP_TAILS_BAR_LENGTH if cls.RECORD_CLIP_TAILS else 0

    @classmethod
    @save_to_song_data
    def toggle_record_clip_tails(cls):
        # type: () -> None
        cls.RECORD_CLIP_TAILS = not cls.RECORD_CLIP_TAILS
        from protocol0 import Protocol0

        Protocol0.SELF.show_message("Record clip tails %s (%s)" % ("ON" if cls.RECORD_CLIP_TAILS else "OFF", cls.SELECTED_CLIP_TAILS_BAR_LENGTH))

    @classmethod
    @save_to_song_data
    def scroll_clip_tails_bar_lengths(cls, go_next):
        # type: (bool) -> None
        cls.RECORD_CLIP_TAILS = True
        enum_values = [enum for enum in list(RecordingTimeEnum) if enum != RecordingTimeEnum.UNLIMITED]
        cls.SELECTED_CLIP_TAILS_BAR_LENGTH = scroll_values(
            enum_values, cls.SELECTED_CLIP_TAILS_BAR_LENGTH, go_next
        )
        cls.show_selected_bar_length("CLIP TAIL", cls.SELECTED_CLIP_TAILS_BAR_LENGTH)

    @classmethod
    @save_to_song_data
    def toggle_protected_mode(cls):
        # type: () -> None
        cls.PROTECTED_MODE_ACTIVE = not cls.PROTECTED_MODE_ACTIVE
        from protocol0 import Protocol0

        Protocol0.SELF.show_message("Protected mode %s" % ("ON" if cls.PROTECTED_MODE_ACTIVE else "OFF"))

    @classmethod
    @save_to_song_data
    def scroll_recording_time(cls, go_next):
        # type: (bool) -> None
        cls.SELECTED_RECORDING_TIME = scroll_values(
            list(RecordingTimeEnum), cls.SELECTED_RECORDING_TIME, go_next
        )
        cls.show_selected_bar_length("RECORDING", cls.SELECTED_RECORDING_TIME.value)

    @classmethod
    def show_selected_bar_length(cls, title, time):
        # type: (str, StringOrNumber) -> None
        if isinstance(time, str):
            time_legend = time
        else:
            time_legend = "%s bar%s" % (time, "s" if abs(time) != 1 else "")
        from protocol0 import Protocol0

        Protocol0.SELF.show_message("Selected %s : %s" % (title, time_legend))
