import json
import os
import sys
from os.path import dirname

root_dir = dirname(os.path.realpath(__file__))

if sys.version_info.major == 2:
    sys.path.insert(0, "%s\\venv\\Lib\\site-packages" % root_dir)

live_environment_loaded = "Live" in sys.modules

from typing import Any, Iterator, Tuple  # noqa: E402


def load_dotenv():
    # type: () -> None
    """ doing this manually because dotenv throws an encoding error """
    with open("%s/.env.json" % root_dir) as f:
        env_vars = json.loads(f.read())
        for key, value in env_vars.iteritems():
            os.environ[key] = str(value)


if sys.version_info.major == 2:
    load_dotenv()


class EmptyModule(object):
    def __init__(self, is_false=True):
        # type: (bool) -> None
        self.is_false = is_false

    def __ne__(self, other):
        # type: (object) -> bool
        return False

    def __eq__(self, other):
        # type: (object) -> bool
        return False

    def __nonzero__(self):
        # type: () -> bool
        """ allows Live environment check """
        return not self.is_false

    def __ge__(self, other):
        # type: (Any) -> bool
        """ allows Live environment check """
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
        # type: () -> Iterator[Tuple[int, int]]
        # that's for push2 scales check
        return iter([(0, 0)])


# allows accessing code from this module from outside of the Live python environment, e.g. Jupyter tests
if not live_environment_loaded:
    sys.modules["Live"] = EmptyModule()  # type: ignore[assignment]
    sys.modules["MidiRemoteScript"] = EmptyModule()  # type: ignore[assignment]
    sys.modules["multipledispatch"] = EmptyModule()  # type: ignore[assignment]

if sys.version_info.major == 2:
    from protocol0.Protocol0 import Protocol0  # noqa: E402

    Protocol0.LIVE_ENVIRONMENT_LOADED = live_environment_loaded


def create_instance(c_instance):  # noqa
    # type: (Any) -> Protocol0
    return Protocol0(c_instance)
