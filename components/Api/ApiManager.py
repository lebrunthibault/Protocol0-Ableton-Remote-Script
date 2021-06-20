import subprocess

import openapi_client
from openapi_client.api.default_api import DefaultApi
from typing import Any
from urllib3.exceptions import MaxRetryError

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.components.Api.ActionMapper import ActionMapper
from a_protocol_0.consts import P0_SYSTEM_DIR
from a_protocol_0.utils.decorators import poll


class ApiManager(AbstractControlSurfaceComponent):
    HOST = "http://127.0.0.1:8000"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ApiManager, self).__init__(*a, **k)
        self._server_started = False
        self.client = DefaultApi(openapi_client.ApiClient())
        self.action_mapper = ActionMapper()

    def initiate_connection(self):
        # type: () -> None
        if not self._server_up():
            pass
            # self.parent.log_info("launching server")
            # subprocess.Popen(P0_SYSTEM_DIR + "\\start_server.bat", shell=True)
        self._server_started = True

        # self._poll_for_actions()

        return None

    @poll
    def _poll_for_actions(self):
        # type: () -> None
        """ Channel for server -> script communication via polling """
        action = self.client.action()
        self.action_mapper.execute(action)

        return None

    def _server_up(self):
        # type: () -> bool
        try:
            self.client.health(_request_timeout=1)
            return True
        except MaxRetryError:
            self.parent.log_error("Server is not up")
            return False
