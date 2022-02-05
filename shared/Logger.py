from typing import Any


class Logger(object):
    """ Facade for logging """

    @classmethod
    def log_dev(cls, *a, **k):
        # type: (Any, Any) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.log_dev(*a, **k)

    @classmethod
    def log_debug(cls, *a, **k):
        # type: (Any, Any) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.log_debug(*a, **k)

    @classmethod
    def log_info(cls, *a, **k):
        # type: (Any, Any) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.log_info(*a, **k)

    @classmethod
    def log_warning(cls, *a, **k):
        # type: (Any, Any) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.log_warning(*a, **k)

    @classmethod
    def log_error(cls, *a, **k):
        # type: (Any, Any) -> None
        from protocol0 import Protocol0
        Protocol0.SELF.log_error(*a, **k)
