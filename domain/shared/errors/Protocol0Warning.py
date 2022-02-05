from typing import Optional, Any


class Protocol0Warning(RuntimeError):
    def __init__(self, message=None, *a):
        # type: (Optional[Any], Any) -> None
        message = message or self.__class__.__name__
        super(Protocol0Warning, self).__init__(message, *a)
