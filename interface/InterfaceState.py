from protocol0.components.SongDataManager import save_song_data, song_synchronizable_class
from protocol0.enums.BarLengthEnum import BarLengthEnum
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.utils.utils import scroll_values


@song_synchronizable_class
class InterfaceState(object):
    SELECTED_RECORDING_BAR_LENGTH = BarLengthEnum.UNLIMITED
    SELECTED_DUPLICATE_SCENE_BAR_LENGTH = BarLengthEnum.FOUR

    RECORD_CLIP_TAILS = False  # records one more bar of audio to make editing easier
    SELECTED_CLIP_TAILS_BAR_LENGTH = BarLengthEnum.ONE

    CURRENT_RECORD_TYPE = RecordTypeEnum.NORMAL

    PROTECTED_MODE_ACTIVE = True  # protected mode prevents certain actions to be made

    # NB: for an unknown reason clip.view.show_envelope does not always show the envelope
    # when the button was not clicked. As a workaround we click it the first time
    CLIP_ENVELOPE_SHOW_BOX_CLICKED = False
    HANDLE_TRACK_NAMES = True

    @classmethod
    @save_song_data
    def scroll_recording_time(cls, go_next):
        # type: (bool) -> None
        cls.SELECTED_RECORDING_BAR_LENGTH = scroll_values(
            list(BarLengthEnum), cls.SELECTED_RECORDING_BAR_LENGTH, go_next
        )
        cls.show_selected_bar_length("RECORDING", cls.SELECTED_RECORDING_BAR_LENGTH)

    @classmethod
    @save_song_data
    def scroll_duplicate_scene_bar_lengths(cls, go_next):
        # type: (bool) -> None
        from protocol0 import Protocol0
        selected_scene = Protocol0.SELF.song.selected_scene
        if selected_scene.length < 2:
            Protocol0.SELF.log_warning(
                "Cannot partial duplicate scene with length %s (min 2 bars)" % selected_scene.length)
            return
        bar_lengths = []
        power = 0
        while pow(2, power) <= selected_scene.bar_length / 2:
            bar_lengths += [pow(2, power), -pow(2, power)]
            power += 1
        bar_lengths.sort()

        cls.SELECTED_DUPLICATE_SCENE_BAR_LENGTH = scroll_values(
            bar_lengths, cls.SELECTED_DUPLICATE_SCENE_BAR_LENGTH, go_next
        )
        cls.show_selected_bar_length("SCENE DUPLICATE", cls.SELECTED_DUPLICATE_SCENE_BAR_LENGTH)

    @classmethod
    def record_clip_tails_length(cls):
        # type: () -> int
        return cls.SELECTED_CLIP_TAILS_BAR_LENGTH.value if cls.RECORD_CLIP_TAILS else 0

    @classmethod
    @save_song_data
    def toggle_record_clip_tails(cls):
        # type: () -> None
        cls.RECORD_CLIP_TAILS = not cls.RECORD_CLIP_TAILS
        from protocol0 import Protocol0

        Protocol0.SELF.show_message("Record clip tails %s (%s)" % (
            "ON" if cls.RECORD_CLIP_TAILS else "OFF", cls.SELECTED_CLIP_TAILS_BAR_LENGTH))

    @classmethod
    @save_song_data
    def scroll_clip_tails_bar_lengths(cls, go_next):
        # type: (bool) -> None
        cls.RECORD_CLIP_TAILS = True
        enum_values = [enum for enum in list(BarLengthEnum) if enum != BarLengthEnum.UNLIMITED]
        cls.SELECTED_CLIP_TAILS_BAR_LENGTH = scroll_values(
            enum_values, cls.SELECTED_CLIP_TAILS_BAR_LENGTH, go_next
        )
        cls.show_selected_bar_length("CLIP TAIL", cls.SELECTED_CLIP_TAILS_BAR_LENGTH)

    @classmethod
    @save_song_data
    def toggle_protected_mode(cls):
        # type: () -> None
        cls.PROTECTED_MODE_ACTIVE = not cls.PROTECTED_MODE_ACTIVE
        from protocol0 import Protocol0

        Protocol0.SELF.show_message("Protected mode %s" % ("ON" if cls.PROTECTED_MODE_ACTIVE else "OFF"))

    @classmethod
    def show_selected_bar_length(cls, title, bar_length):
        # type: (str, BarLengthEnum) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.show_message("Selected %s : %s" % (title, bar_length))
