import json

from typing import Optional, Dict, Any

from protocol0.application.midi_api.ApiError import ApiError
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.application.midi_api.decorators import EXPOSED_P0_METHODS
from protocol0.domain.shared.utils import find_if, get_callable_repr
from protocol0.shared.Logger import Logger


class ApiAction(object):
    _EXPOSED_P0_CALLABLES = None  # type: Optional[Dict]

    def __init__(self, method_name, args):
        # type: (str, Dict) -> None
        if not self._EXPOSED_P0_CALLABLES:
            self._create_method_mapping()

        if not isinstance(method_name, basestring):
            raise ApiError(
                "Type error on method_name while instating ApiAction, expected basestring got %s" % type(method_name))
        if not isinstance(args, Dict):
            raise ApiError("Type error on args while instating ApiAction, expected list got %s" % type(args))
        if method_name not in self._EXPOSED_P0_CALLABLES:
            raise ApiError("%s is not a valid method name" % method_name)
        self.method = self._EXPOSED_P0_CALLABLES[method_name]
        self.args = args

    @classmethod
    def _create_method_mapping(cls):
        # type: () -> None
        """ moving from method names to real methods by looking up components or instantiating them"""
        if cls._EXPOSED_P0_CALLABLES:
            return

        cls._EXPOSED_P0_CALLABLES = {}
        for method_name, class_instance in EXPOSED_P0_METHODS.items():
            method = cls._get_method_from_method_name_and_class(class_instance, method_name)
            cls._EXPOSED_P0_CALLABLES[method_name] = method

    @classmethod
    def _get_method_from_method_name_and_class(cls, class_instance, method_name):
        # type: (Any, str) -> Any
        from protocol0 import Protocol0
        component = find_if(lambda c: c.__class__ == class_instance, Protocol0.SELF.components)
        if component:
            return getattr(component, method_name)
        else:
            raise Protocol0Error("You should create the method mapping after the components instantiation. Failed for %s.%s" % (class_instance, method_name))

    @classmethod
    def make_from_string(cls, payload):
        # type: (str) -> ApiAction
        try:
            data = json.loads(payload)
        except ValueError:
            raise ApiError("json decode error on string : %s" % payload)

        try:
            return ApiAction(method_name=data["method"], args=data["args"])
        except (KeyError, TypeError) as e:
            raise ApiError("Invalid string payload %s (%s)" % (payload, e))

    def execute(self):
        # type: () -> None
        Logger.log_debug("Api call, executing %s" % get_callable_repr(self.method))
        self.method(**self.args)
