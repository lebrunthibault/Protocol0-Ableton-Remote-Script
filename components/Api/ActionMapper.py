from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.components.SearchManager import SearchManager
from a_protocol_0.enums.ServerActionEnum import ServerActionEnum
from openapi_client import Action


class ActionMapper(AbstractControlSurfaceComponent):
    server_action_mappings = {ServerActionEnum.SEARCH_TRACK: SearchManager.search_track}

    def execute(self, action):
        # type: (Action) -> None
        if not action.enum:
            return None

        if action.enum not in self.server_action_mappings:
            self.parent.log_error("ServerActionEnum is not configured: %s" % action.enum)
            return None

        func = self.server_action_mappings[action.enum]
        args = (action.arg) if action.arg else ()

        self.parent.log_notice("executing method %s with args %s" % (func, args))
        func(*args)

        return None
