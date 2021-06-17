from openapi_client import Action
from typing import Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.enums.ServerActionEnum import ServerActionEnum


class ActionMapper(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionMapper, self).__init__(*a, **k)
        self._server_action_mappings = {ServerActionEnum.SEARCH_TRACK: self.parent.searchManager.search_track}

    def execute(self, action):
        # type: (Action) -> None
        if not action.enum:
            return None

        if action.enum not in self._server_action_mappings:
            self.parent.log_error("ServerActionEnum is not configured: %s" % action.enum)
            return None

        func = self._server_action_mappings[action.enum]
        args = (action.arg,) if action.arg else ()

        self.parent.log_notice("executing method %s with args %s" % (func, args))
        func(*args)

        return None
