import json
import urllib
import urllib2

import openapi_client
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.components.Api.ActionMapper import ActionMapper
from a_protocol_0.consts import P0_SYSTEM_DIR
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.utils.decorators import poll
from openapi_client.api.default_api import DefaultApi
from typing import Dict, Optional, Any
from urllib3.exceptions import MaxRetryError


class ApiManager(AbstractControlSurfaceComponent):
    HOST = "http://127.0.0.1:8000"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ApiManager, self).__init__(*a, **k)
        self._server_started = False
        self.client = DefaultApi(openapi_client.ApiClient())
        self.action_mapper = ActionMapper()

    def get(self, path, **params):
        # type: (str, Dict) -> Optional[Any]
        if not self._server_started or not self.parent.started:
            return None

        try:
            res = urllib2.urlopen("%s/action?%s" % (self.HOST, urllib.urlencode(params)))
            self.parent.log_info("GET %s %s s" % (path, res.getcode()))  # type: ignore

            try:
                json_content = json.loads(res.read())
            except (TypeError, ValueError) as e:
                raise Protocol0Error("Invalid json : %s" % e)

            if "res" not in json_content:
                raise Protocol0Error(
                    "invalid json structure received from server (missing 'action' property) : %s" % json_content
                )

            return json_content["res"]
        except urllib2.URLError as e:
            raise Protocol0Error("GET %s, error: %s" % (path, e))

    def initiate_connection(self):
        # type: () -> None
        if not self._server_up():
            self.parent.log_info("launching server")
            self.parent.commandManager.execute_batch(P0_SYSTEM_DIR + "\\start.bat")
        self._server_started = True

        self._poll_for_actions()

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
        except MaxRetryError:
            self.parent.log_error("Server is not up")
            return False
