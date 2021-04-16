import abc
from collections import MutableSequence

from typing import List, Any

from _Framework.SubjectSlot import SubjectMeta
from a_protocol_0.lom.AbstractObject import AbstractObject


class CombinedMeta(SubjectMeta, abc.ABCMeta):
    """
        makes it possible to inherit both from AbstractObject and class defining
        abc.ABCMeta as its meta class
    """
    pass


class UserMutableSequence(MutableSequence, AbstractObject):
    __metaclass__ = CombinedMeta

    """
        base class for defining custom list classes
    """

    def __init__(self, list, *a, **k):
        # type: (List[Any]) -> None
        super(UserMutableSequence, self).__init__(*a, **k)
        self._list = list

    def __getitem__(self, value):
        return self._list[value]

    def __delitem__(self, value):
        self._list.remove(value)

    def __setitem__(self, value):
        if value in self:
            return
        self._list.append(value)

    def insert(self, index, value):
        self._list.insert(index, value)

    def __iter__(self):
        return iter(self._list)

    def __len__(self):
        return len(self._list)
