import json
import urllib2

from typing import Dict, Optional

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.enums.ServerActionEnum import ServerActionEnum
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.utils.decorators import poll


class HttpClient(AbstractControlSurfaceComponent):
    @poll
    def poll(self):
        # type: () -> None
        try:
            contents = urllib2.urlopen("http://127.0.0.1:8000/action").read()
        except urllib2.URLError as e:
            self.parent.log_error("URLError : %s" % e)
            return

        if not self.parent.started:
            return

        if contents:
            try:
                json_content = json.loads(contents)
            except (TypeError, ValueError) as e:
                raise Protocol0Error("Invalid json : %s" % e)

            if "action" not in json_content:
                raise Protocol0Error(
                    "invalid json structure received from server (missing 'action' property) : %s" % json_content
                )

            self.dispatch_action(json_content)
            self.parent.log_dev("got json action %s" % json_content)
        else:
            print("No action")

    def dispatch_action(self, json_content):
        # type: (Dict) -> None
        action = ServerActionEnum.get_from_value(json_content["action"])  # type: Optional[ServerActionEnum]

        if action is None:
            raise Protocol0Error("invalid action received from server : %s" % json_content)

        args = ()

        if "arg" in json_content:
            args = (json_content["arg"],)

        func = getattr(self.parent.searchManager, action.get_method_name())

        self.parent.log_notice("executing method %s with args %s" % (func, args))
        func(*args)
