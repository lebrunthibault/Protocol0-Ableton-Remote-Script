from typing import Any, Optional

from protocol0.application.command.SerializableCommand import SerializableCommand


class ProcessBackendResponseCommand(SerializableCommand):
    def __init__(self, res, res_type=None):
        # type: (Any, Optional[str]) -> None
        super(ProcessBackendResponseCommand, self).__init__()
        self.res = res
        self.res_type = res_type
