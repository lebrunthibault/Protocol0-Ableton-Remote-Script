from typing import List, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from protocol0.domain.lom.device.DeviceEnum import DeviceEnum


class DeviceEnumGroup(object):
    def __init__(self, name, enums):
        # type: (str, List[DeviceEnum]) -> None
        self.name = name
        self.enums = enums

    def __repr__(self):
        # type: () -> str
        return "DeviceEnumGroup('%s')" % self.name

    def to_dict(self):
        # type: () -> Dict
        return {
            "name": self.name,
            "devices": [d.name for d in self.enums]
        }
