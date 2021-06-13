import json
import urllib
import urllib2

import openapi_client
from openapi_client.api.default_api import DefaultApi
from typing import Dict, Optional, Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import SERVER_DIR
from a_protocol_0.enums.ServerActionEnum import ServerActionEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.utils.decorators import poll


class ApiManager(AbstractControlSurfaceComponent):
    HOST = "http://127.0.0.1:8000"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ApiManager, self).__init__(*a, **k)
        self._started = False
        self.client = DefaultApi(openapi_client.ApiClient())

    def get(self, path, **params):
        # type: (str, Dict) -> Optional[Any]
        if not self._started or not self.parent.started:
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

    def start_server(self):
        # type: () -> None
        try:
            urllib2.urlopen(self.client.index())
        except urllib2.URLError:
            self.parent.commandManager.execute_batch(SERVER_DIR + "\\start.bat")

        self._started = True

    @poll
    def poll_for_actions(self):
        # type: () -> None
        response = self.client.action()
        if not response["action"]:
            return None

        action = ServerActionEnum.get_from_value(response["action"])  # type: Optional[ServerActionEnum]

        if action is None:
            raise Protocol0Error("invalid action received from server : %s" % response)

        args = []

        if "arg" in response:
            args.append(response["arg"])

        # func = getattr(self.parent.searchManager, action.get_method_name())
        func = action.value

        self.parent.log_notice("executing method %s with args %s" % (func, args))
        func(*args)
