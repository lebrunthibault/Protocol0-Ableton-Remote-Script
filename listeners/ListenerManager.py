from typing import TYPE_CHECKING

from a_protocol_0.Protocol0ComponentMixin import Protocol0ComponentMixin

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.Protocol0Component import Protocol0Component


class ListenerManager(Protocol0ComponentMixin):
    def __init__(self, *a, **k):
        super(ListenerManager, self).__init__(*a, **k)
