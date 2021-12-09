from abc import abstractmethod

from typing import Any, Optional

from protocol0.lom.AbstractObject import AbstractObject
from protocol0.utils.decorators import p0_subject_slot


class AbstractObjectName(AbstractObject):
    NAME_BLACKLIST = ("audio", "midi")

    def __init__(self, obj, *a, **k):
        # type: (AbstractObject, Any, Any) -> None
        super(AbstractObjectName, self).__init__(*a, **k)
        self._obj = obj
        self._base_name = None  # type: Optional[str]

    @property
    def base_name(self):
        # type: () -> str
        """ lazy loading """
        if self._base_name is None:
            self._base_name = self._get_base_name()
        return self._base_name

    @base_name.setter
    def base_name(self, base_name):
        # type: (str) -> None
        self._base_name = base_name

    @abstractmethod
    def _get_base_name(self):
        # type: () -> str
        raise NotImplementedError

    @abstractmethod
    def update(self):
        # type: () -> str
        raise NotImplementedError

    def normalize_base_name(self):
        # type: () -> None
        if self.base_name.lower() in self.NAME_BLACKLIST:
            self.base_name = ""
        try:
            _ = int(self.base_name)
            self.base_name = ""
        except ValueError:
            pass

    @p0_subject_slot("name")
    def _name_listener(self, force=False):
        # type: (bool) -> None
        """ overridden """
        base_name = self._get_base_name()
        # noinspection PyUnresolvedReferences
        if not force and base_name == self.base_name and self._obj.name != base_name:
            return
        self.base_name = base_name
        self.normalize_base_name()
        self.parent.defer(self.update)
