from typing import Optional, Any

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


class Protocol0Warning(Protocol0Error):
    def __init__(self, message=None, *a):
        # type: (Optional[Any], Any) -> None
        message = message or self.__class__.__name__
        super(Protocol0Warning, self).__init__(message, *a)
