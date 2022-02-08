from protocol0.domain.command.SaveSongDataCommand import SaveSongDataCommand
from protocol0.domain.enums.BarLengthEnum import BarLengthEnum
from protocol0.domain.shared.CommandBus import CommandBus
from protocol0.domain.shared.utils import scroll_values
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.StatusBar import StatusBar


class InterfaceState(object):
    SELECTED_RECORDING_BAR_LENGTH = BarLengthEnum.UNLIMITED
    SELECTED_DUPLICATE_SCENE_BAR_LENGTH = 4

    FOCUS_PROPHET_ON_STARTUP = False

    @classmethod
    def scroll_recording_time(cls, go_next):
        # type: (bool) -> None
        cls.SELECTED_RECORDING_BAR_LENGTH = scroll_values(
            list(BarLengthEnum), cls.SELECTED_RECORDING_BAR_LENGTH, go_next
        )
        StatusBar.show_message("SCENE RECORDING : %s" % cls.SELECTED_RECORDING_BAR_LENGTH)
        CommandBus.dispatch(SaveSongDataCommand())

    @classmethod
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

        from protocol0.domain.lom.scene.Scene import Scene
        Scene.SELECTED_DUPLICATE_SCENE_BAR_LENGTH = scroll_values(
            bar_lengths, Scene.SELECTED_DUPLICATE_SCENE_BAR_LENGTH, go_next
        )
        StatusBar.show_message("SCENE DUPLICATE : %s" % Scene.SELECTED_DUPLICATE_SCENE_BAR_LENGTH)
        CommandBus.dispatch(SaveSongDataCommand())
