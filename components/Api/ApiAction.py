import json

from a_protocol_0.errors.ApiError import ApiError
from a_protocol_0.utils.decorators import EXPOSED_P0_METHODS
from a_protocol_0.utils.log import log_ableton
from a_protocol_0.utils.utils import find_if
from typing import List, Optional, Dict


class ApiAction():
    EXPOSED_P0_CALLABLES = None  # type: Optional[Dict]

    def __init__(self, method_name, args):
        # type: (str, List) -> None
        if not self.EXPOSED_P0_CALLABLES:
            raise ApiError("The method mapping is not done")
        if not isinstance(method_name, basestring):
            raise ApiError(
                "Type error on method_name while instating ApiAction, expected basestring got %s" % type(method_name))
        if not isinstance(args, Dict):
            raise ApiError("Type error on args while instating ApiAction, expected list got %s" % type(args))
        if method_name not in self.EXPOSED_P0_CALLABLES:
            raise ApiError("%s is not a valid method name" % method_name)
        self.method = self.EXPOSED_P0_CALLABLES[method_name]
        self.args = args

    @classmethod
    def create_method_mapping(cls):
        """ moving from method names to real methods by looking up components or instantiating them"""
        if cls.EXPOSED_P0_CALLABLES:
            return

        cls.EXPOSED_P0_CALLABLES = {}
        for method_name, class_instance in EXPOSED_P0_METHODS.items():
            method = cls._get_method_from_method_name_and_class(class_instance, method_name)
            cls.EXPOSED_P0_CALLABLES[method_name] = method

    @classmethod
    def _get_method_from_method_name_and_class(cls, class_instance, method_name):
        from a_protocol_0 import Protocol0
        component = find_if(lambda c: c.__class__ == class_instance, Protocol0.SELF.components)
        if component:
            return getattr(component, method_name)
        else:
            with Protocol0.SELF.component_guard():
                return getattr(class_instance(), method_name)

    @classmethod
    def make_from_string(cls, payload):
        # type: (str) -> ApiAction
        try:
            dict = json.loads(payload)
            log_ableton(payload)
        except ValueError:
            raise ApiError("json decode error on string : %s" % payload)

        try:
            return ApiAction(method_name=dict["method"], args=dict["args"])
        except (KeyError, TypeError) as e:
            raise ApiError("Invalid string payload %s (%s)" % (payload, e))

    def execute(self):
        from a_protocol_0 import Protocol0
        Protocol0.SELF.log_info("Executing method %s from Api call" % self.method)
        self.method(**self.args)
