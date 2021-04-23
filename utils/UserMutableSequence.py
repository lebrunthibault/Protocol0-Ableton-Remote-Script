import abc
from collections import MutableSequence

from typing import List, Any, Iterator, Union

from _Framework.SubjectSlot import SubjectMeta
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.my_types import T


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
        # type: (List[T], Any, Any) -> None
        super(UserMutableSequence, self).__init__(*a, **k)
        self._list = list

    def __getitem__(self, value):
        # type: (Union[int, slice]) -> Union[T, List[T]]
        return self._list[value]

    def __delitem__(self, value):
        # type: (T) -> None
        self._list.remove(value)

    def __setitem__(self, index, value):
        # type: (Union[int, slice], T) -> None
        if value in self or not isinstance(index, int):
            return None
        self._list[index] = value

    def insert(self, index, value):
        # type: (int, T) -> None
        self._list.insert(index, value)

    def __iter__(self):
        # type: () -> Iterator[T]
        return iter(self._list)

    def __len__(self):
        # type: () -> int
        return len(self._list)
