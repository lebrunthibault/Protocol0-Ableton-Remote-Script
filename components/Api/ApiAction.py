import json

from a_protocol_0.errors.ApiError import ApiError
from a_protocol_0.utils.decorators import EXPOSED_P0_METHODS
from a_protocol_0.utils.utils import find_if
from typing import Dict


class ApiAction():
    def __init__(self, method_name, args):
        # type: (str, Dict) -> None
        if not (isinstance(method_name, str) and isinstance(args, Dict)):
            raise ApiError("Type error while instating ApiAction")
        self.method = find_if(lambda method: method.__name__ == method_name, EXPOSED_P0_METHODS)
        if not self.method:
            raise ApiError("%s is not a valid method name" % method_name)
        self.args = args

    @staticmethod
    def make_from_string(payload):
        # type: (str) -> ApiAction
        try:
            dict = json.loads(payload)
        except ValueError:
            raise ApiError("json decode error on string : %s" % payload)
        try:
            return ApiAction(method_name=dict["method"], args=dict["args"])
        except KeyError as e:
            raise ApiError("Invalid string payload : %s" % e.message)

    def execute(self):
        self.method(*self.args)
