import json
import os
import sys
from os.path import dirname

if sys.version_info.major == 2:
    sys.path.insert(0, "%s\\venv\\Lib\\site-packages" % dirname(os.path.realpath(__file__)))

live_environment_loaded = "Live" in sys.modules

from typing import Any, Iterator  # noqa: E402


def load_dotenv():
    # type: () -> None
    """doing this manually because dotenv throws an encoding error"""
    with open("%s/.env.json" % dirname(os.path.realpath(__file__))) as f:
        env_vars = json.loads(f.read())
        for key, value in env_vars.iteritems():
            os.environ[key] = str(value)


if sys.version_info.major == 2:
    load_dotenv()


class EmptyModule(object):
    def __init__(self, name="", is_false=True):
        # type: (str, bool) -> None
        self.name = name
        self.is_false = is_false

    def __ne__(self, other):
        # type: (object) -> bool
        return False

    def __eq__(self, other):
        # type: (object) -> bool
        return False

    def __nonzero__(self):
        # type: () -> bool
        """allows Live environment check"""
        return not self.is_false

    def __ge__(self, other):
        # type: (Any) -> bool
        """allows Live environment check"""
        return False

    def __call__(self, *a, **k):
        # type: (Any, Any) -> EmptyModule
        return self

    def __getattr__(self, name):
        # type: (Any) -> EmptyModule
        return self

    def __hash__(self):
        # type: () -> int
        return 0

    def __iter__(self):
        # type: () -> Iterator
        """Handles push2 scales"""
        return iter([("", "")])


# allows accessing lint from this module from outside the Live python environment
if not live_environment_loaded:
    sys.modules["Live"] = EmptyModule("Live")
    sys.modules["MidiRemoteScript"] = EmptyModule("MidiRemoteScript")
    sys.modules["multipledispatch"] = EmptyModule("multipledispatch")


def create_instance(c_instance):  # noqa
    # type: (Any) -> Any
    from protocol0.application.Protocol0 import Protocol0

    return Protocol0(c_instance)
