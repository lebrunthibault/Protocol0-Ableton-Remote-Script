from typing import Any, Dict

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.enums.ServerActionEnum import ServerActionEnum


class ApiManager(AbstractControlSurfaceComponent):
    EXPOSED_METHODS = []
    
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ApiManager, self).__init__(*a, **k)
        self._server_action_mappings = {ServerActionEnum.SEARCH_TRACK: self.parent.searchManager.search_track}

    def execute_action_from_api(self, action):
        # type: (Dict) -> None
        if not action.get("enum"):
            return None

        server_action_enum = ServerActionEnum.get_from_value(action["enum"])
        if server_action_enum not in self._server_action_mappings:
            self.parent.log_error("ServerActionEnum is not configured: %s" % action["enum"])
            return None

        func = self._server_action_mappings[server_action_enum]
        args = (action.get("arg"),) if action.get("arg") else ()

        self.parent.log_notice("executing method %s with args %s" % (func, args))
        func(*args)

        return None
