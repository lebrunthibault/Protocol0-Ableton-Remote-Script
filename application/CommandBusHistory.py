import time

from typing import List, Optional, Type

from protocol0.application.command.SerializableCommand import SerializableCommand


class HistoryEntry(object):
    def __init__(self, command):
        # type: (SerializableCommand) -> None
        self.command = command
        self.executed_at = time.time()


class CommandBusHistory(object):
    _SIZE = 20

    def __init__(self):
        # type: () -> None
        self._history = [None] * self._SIZE  # type: List[Optional[HistoryEntry]]

    def push(self, command):
        # type: (SerializableCommand) -> None
        """Expect only increasing time.time"""
        self._history.append(HistoryEntry(command))

        # rotate history
        self._history = self._history[-20:]

    def has_recent_command(self, command_class, delay):
        # type: (Type[SerializableCommand], int) -> bool
        """Delay in ms"""
        time_limit = time.time() - delay

        for entry in reversed(filter(None, self._history)):
            if entry.executed_at < time_limit:
                return False
            if isinstance(entry.command, command_class):
                return True

        return False
