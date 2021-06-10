import json
import urllib
import urllib2

from typing import Dict, Optional, Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.consts import SERVER_DIR
from a_protocol_0.enums.ServerActionEnum import ServerActionEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.utils.decorators import poll


class HttpClient(AbstractControlSurfaceComponent):
    HOST = "http://127.0.0.1:8000"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(HttpClient, self).__init__(*a, **k)
        self._started = False

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
            urllib2.urlopen(self.HOST + "/action")
        except urllib2.URLError:
            self.parent.commandManager.execute_batch(SERVER_DIR + "\\start.bat")

        self._started = True

    @poll
    def poll_for_actions(self):
        # type: () -> None
        contents = self.get("/action")

        if not contents:
            return

        if "action" not in contents:
            raise Protocol0Error(
                "invalid json structure received from server (missing 'action' property) : %s" % contents
            )

        self.parent.log_dev("got action %s" % contents)
        self._dispatch_action(contents)

    def _dispatch_action(self, json_content):
        # type: (Dict) -> None
        action = ServerActionEnum.get_from_value(json_content["action"])  # type: Optional[ServerActionEnum]

        if action is None:
            raise Protocol0Error("invalid action received from server : %s" % json_content)

        args = []

        if "arg" in json_content:
            args.append(json_content["arg"])

        func = getattr(self.parent.searchManager, action.get_method_name())

        self.parent.log_notice("executing method %s with args %s" % (func, args))
        func(*args)
