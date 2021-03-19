from typing import TYPE_CHECKING

from a_protocol_0.lom.ObjectSynchronizer import ObjectSynchronizer
from a_protocol_0.lom.clip.AbstractAutomationClip import AbstractAutomationClip
from a_protocol_0.lom.clip.AutomationClipName import AutomationClipName

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.Clip import Clip


class ClipSynchronizer(ObjectSynchronizer):
    def __init__(self, master, slave, *a, **k):
        # type: (Clip, Clip) -> None
        super(ClipSynchronizer, self).__init__(master, slave, "_clip", *a, **k)
        self.master = self.master  # type: Clip
        self.slave = self.slave  # type: Clip

        master.linked_clip = slave
        slave.linked_clip = master

        slave.clip_name = master.clip_name

        if isinstance(master, AbstractAutomationClip):
            master.clip_name = slave.clip_name = AutomationClipName(master)

        # noinspection PyUnresolvedReferences
        master.notify_linked()
        # noinspection PyUnresolvedReferences
        slave.notify_linked()

    def disconnect(self):
        super(ClipSynchronizer, self).disconnect()
        self.master.linked_clip = self.slave.linked_clip = None
