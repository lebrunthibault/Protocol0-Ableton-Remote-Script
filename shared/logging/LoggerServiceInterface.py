from typing import Any, Optional

from protocol0.shared.logging.LogLevelEnum import LogLevelEnum


class LoggerServiceInterface(object):
    def log(self, message, debug=True, level=None):
        # type: (Any, bool, Optional[LogLevelEnum]) -> None
        pass
