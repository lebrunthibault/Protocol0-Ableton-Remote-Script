import re

from typing import Any, Optional

from protocol0.domain.shared.utils.utils import smart_string


class InstrumentPreset(object):
    def __init__(self, index, name, category=None):
        # type: (int, Optional[basestring], Optional[str]) -> None
        self.index = index
        name = smart_string(name) if name else None
        self.original_name = name
        self.name = self._format_name(name)
        self.category = category.lower() if category else ""

    def __repr__(self, **k):
        # type: (Any) -> str
        name = "%s (%s)" % (self.name, self.index + 1)
        if self.category:
            name += "(%s)" % self.category
        return name

    def _format_name(self, name):
        # type: (Optional[str]) -> str
        if name is None:
            return "empty"

        base_preset_name = re.sub('\\.[a-z0-9]{2,4}', '', name)  # remove file extension
        return str(base_preset_name)
