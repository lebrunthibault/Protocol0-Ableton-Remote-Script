import sys

sys.path.insert(0, "C:\\Python27\\Lib\\site-packages")
live_environment_loaded = "Live" in sys.modules

from typing import Literal, Any, Iterator, Tuple  # noqa: E402


class EmptyModule(object):
    def __init__(self, is_false=True):
        # type: (bool) -> None
        self.is_false = is_false

    def __ne__(self, other):
        # type: (object) -> Literal[False]
        return False

    def __eq__(self, other):
        # type: (object) -> Literal[False]
        return False

    def __nonzero__(self):
        # type: () -> bool
        """ allows Live environment check """
        return not self.is_false

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

from .Protocol0 import Protocol0  # noqa: E402

Protocol0.LIVE_ENVIRONMENT_LOADED = live_environment_loaded


def create_instance(c_instance):  # noqa
    # type: (Any) -> Protocol0
    return Protocol0(c_instance)
