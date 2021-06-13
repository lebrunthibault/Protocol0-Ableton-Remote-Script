import os
import subprocess

from typing import Any, Optional

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.enums.ColorEnum import InterfaceColorEnum
from a_protocol_0.enums.CommandEnum import CommandEnum
from a_protocol_0.enums.PixelEnum import PixelEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error


class CommandManager(AbstractControlSurfaceComponent):
    def execute(self, command, **k):
        # type: (CommandEnum, Any) -> Any
        return self.parent.apiManager.get(command.name.lower(), **k)

    @classmethod
    def execute_batch(self, filename):
        # type: (str) -> int
        return self._execute_program(None, filename)

    @staticmethod
    def _execute_program(program, filename, *args):
        # type: (Optional[str], str, Any) -> int
        if not os.path.exists(filename):
            raise Protocol0Error("incorrect script path: %s" % filename)

        if program is None:
            subprocess.Popen(filename, shell=True)
            return 0
        else:
            parameters = [program, filename]
            for arg in args:
                parameters.append(str(arg))

            child = subprocess.Popen(parameters)
            child.communicate()
            return child.returncode

    def click(self, x, y):
        # type: (int, int) -> None
        self.execute(CommandEnum.CLICK, x=x, y=y)

    def double_click(self, pixel):
        # type: (PixelEnum) -> None
        self.execute(CommandEnum.DOUBLE_CLICK, x=pixel.value[0], y=pixel.value[1])

    def pixel_has_color(self, pixel, color):
        # type: (PixelEnum, InterfaceColorEnum) -> bool
        (x, y) = pixel.value
        return bool(self.execute(CommandEnum.PIXEL_HAS_COLOR, x=x, y=y, color=color))
