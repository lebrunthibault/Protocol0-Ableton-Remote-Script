from typing import Union

from protocol0.domain.enums.BarLengthEnum import BarLengthEnum
from protocol0.domain.shared.SongFacade import SongFacade
from protocol0.domain.shared.utils import scroll_values
from protocol0.infra.SongDataManager import save_song_data, song_synchronizable_class
from protocol0.infra.log import log_ableton
from protocol0.shared.Logger import Logger


@song_synchronizable_class
class InterfaceState(object):
    SELECTED_RECORDING_BAR_LENGTH = BarLengthEnum.UNLIMITED
    SELECTED_DUPLICATE_SCENE_BAR_LENGTH = 4

    FOCUS_PROPHET_ON_STARTUP = False

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
        selected_scene = SongFacade.selected_scene()
        if selected_scene.length < 2:
            Logger.log_warning(
                "Cannot partial duplicate scene with length %s (min 2 bars)" % selected_scene.length)
            return
        bar_lengths = []
        power = 0
        while pow(2, power) <= selected_scene.bar_length / 2:
            bar_lengths += [pow(2, power), -pow(2, power)]
            power += 1
        bar_lengths.sort()
        log_ableton("bar_lengths: %s" % bar_lengths)

        from protocol0.domain.lom.scene.Scene import Scene
        Scene.SELECTED_DUPLICATE_SCENE_BAR_LENGTH = scroll_values(
            bar_lengths, Scene.SELECTED_DUPLICATE_SCENE_BAR_LENGTH, go_next
        )
        cls.show_selected_bar_length("SCENE DUPLICATE", Scene.SELECTED_DUPLICATE_SCENE_BAR_LENGTH)

    @classmethod
    def show_selected_bar_length(cls, title, bar_length):
        # type: (str, Union[int, BarLengthEnum]) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.show_message("Selected %s : %s" % (title, bar_length))
