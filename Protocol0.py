from __future__ import with_statement

import types

from a_protocol_0.actions.ActionManager import ActionManager

from a_protocol_0.Protocol0Component import Protocol0Component
from a_protocol_0.listeners.ListenerManager import ListenerManager


class Protocol0(Protocol0Component):

    def __init__(self, *a, **k):
        super(Protocol0, self).__init__(*a, **k)
        with self.component_guard():
            # removes double logging
            self._c_instance.log_message = types.MethodType(lambda s, message: None, self._c_instance)
            ActionManager(parent=self)
            ListenerManager(parent=self)
            self.show_message('Protocol0 initiated')
