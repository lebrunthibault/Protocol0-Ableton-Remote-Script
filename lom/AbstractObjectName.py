from typing import Any

from protocol0.lom.AbstractObject import AbstractObject


class AbstractObjectName(AbstractObject):
    NAME_BLACKLIST = ("audio", "midi")

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AbstractObjectName, self).__init__(*a, **k)
        self.base_name = ""

    def normalize_base_name(self):
        # type: () -> None
        self.base_name = self.base_name.split("-")[0].strip()
        if self.base_name.lower() in self.NAME_BLACKLIST:
            self.base_name = ""
        try:
            _ = int(self.base_name)
            self.base_name = ""
        except ValueError:
            pass
