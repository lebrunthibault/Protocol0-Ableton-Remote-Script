import json
from functools import partial

from typing import Dict

from protocol0.enums.LogLevelEnum import LogLevelEnum
from protocol0.errors.ApiError import ApiError
from protocol0.interface.EncoderAction import EncoderAction
from protocol0.utils.decorators import EXPOSED_P0_METHODS
from protocol0.utils.log import log_ableton


class ApiAction(object):
    def __init__(self, method_name, args):
        # type: (str, Dict) -> None
        if not EXPOSED_P0_METHODS:
            raise ApiError("The method mapping is not done")
        if not isinstance(method_name, basestring):
            raise ApiError(
                "Type error on method_name while instantiating ApiAction, expected basestring got %s" % type(
                    method_name))
        if not isinstance(args, Dict):
            raise ApiError("Type error on args while instating ApiAction, expected list got %s" % type(args))
        if method_name not in EXPOSED_P0_METHODS:
            raise ApiError("%s is not a valid method name" % method_name)
        self.method = EXPOSED_P0_METHODS[method_name]
        self.args = args

    @classmethod
    def make_from_string(cls, payload):
        # type: (str) -> ApiAction
        try:
            data = json.loads(payload)
            log_ableton(payload, level=LogLevelEnum.DEBUG)
        except ValueError:
            raise ApiError("json decode error on string : %s" % payload)

        try:
            return ApiAction(method_name=data["method"], args=data["args"])
        except (KeyError, TypeError) as e:
            raise ApiError("Invalid string payload %s (%s)" % (payload, e))

    def execute(self):
        # type: () -> None
        from protocol0 import Protocol0
        Protocol0.SELF.log_debug("Executing method %s from Api call" % self.method)

        EncoderAction(func=partial(self.method, **self.args)).execute(encoder_name="Midi API")
