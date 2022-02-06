from collections import Callable
from types import MethodType

from typing import Any

import Live

from _Framework.ControlSurface import ControlSurface
from protocol0.application.Container import Container
from protocol0.infra.scheduler.Scheduler import Scheduler
from protocol0.shared.Logger import Logger


class Protocol0(ControlSurface):
    CONTAINER = None  # type: Container
    APPLICATION = None  # type: Live.Application.Application
    SHOW_MESSAGE = None  # type: Callable

    def __init__(self, c_instance=None):
        # type: (Any, bool) -> None
        super(Protocol0, self).__init__(c_instance=c_instance)
        Protocol0.APPLICATION = self.application()
        Protocol0.SHOW_MESSAGE = self.show_message

        self.song().stop_playing()  # doing this early because the set often loads playing
        # stop log duplication
        self._c_instance.log_message = MethodType(lambda s, message: None, self._c_instance)  # noqa

        with self.component_guard():
            Protocol0.CONTAINER = Container()
            Protocol0.CONTAINER.build(self)

        self.start()

    def start(self):
        # type: () -> None
        self.CONTAINER.midi_manager.ping_midi_server()

        self.CONTAINER.song_manager.init_song()

        Logger.log_info("Protocol0 script loaded")

    def disconnect(self):
        # type: () -> None
        Scheduler.stop()
        super(Protocol0, self).disconnect()
