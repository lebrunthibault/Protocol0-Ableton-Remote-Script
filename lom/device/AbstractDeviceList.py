from collections import MutableSequence

from typing import Any

from a_protocol_0.utils.UserMutableSequence import UserMutableSequence


class AbstractDeviceList(UserMutableSequence):
    """ Manipulate a track list as an object """

    def __init__(self, devices, *a, **k):
        # type: (MutableSequence, Any, Any) -> None
        devices = list(dict.fromkeys(devices))
        super(AbstractDeviceList, self).__init__(list=devices, *a, **k)
        # self._devices = devices
