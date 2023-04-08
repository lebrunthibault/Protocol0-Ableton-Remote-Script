from contextlib import contextmanager

from typing import Iterator, Optional

from protocol0.application.command.MidiNoteCommand import MidiNoteCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.application.control_surface.EncoderMoveEnum import EncoderMoveEnum
from protocol0.application.control_surface.MultiEncoder import MultiEncoder
from protocol0.domain.shared.utils.list import find_if


@contextmanager
def component_guard():
    # type: () -> Iterator
    # noinspection PyBroadException
    try:
        yield
    except Exception:
        pass


class MidiNoteCommandHandler(CommandHandlerInterface):
    def handle(self, command):
        # type: (MidiNoteCommand) -> None
        action_group_class = find_if(
            lambda a: a.CHANNEL == command.channel, ActionGroupInterface.__subclasses__()
        )

        assert action_group_class is not None, (
            "no action group found for channel %s" % command.channel
        )

        action_group = action_group_class(self._container, component_guard)
        action_group.configure()

        encoder = find_if(
            lambda m: m.identifier == command.note, action_group._multi_encoders
        )  # type: Optional[MultiEncoder]

        assert encoder is not None, "encoder %s not found in action group %s" % (
            command.note,
            action_group,
        )

        encoder._find_and_execute_action(move_type=EncoderMoveEnum.PRESS)
