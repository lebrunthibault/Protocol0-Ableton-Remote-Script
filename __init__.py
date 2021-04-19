import sys

sys.path.insert(0, "C:\\Python27\\Lib\\site-packages")
live_environment_loaded = "Live" in sys.modules


class EmptyModule(object):
    def __init__(self, is_false=True):
        self.is_false = is_false

    def __ne__(self, other):
        return False

    def __eq__(self, other):
        return False

    def __nonzero__(self):
        # allows Live environment check
        return not self.is_false

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        return self

    def __hash__(self):
        return 0

    def __iter__(self):
        # that's for push2 checking scales
        return iter([(0, 0)])


# allows accessing code from this module from outside of the Live python environment, e.g. Jupyter tests
if not live_environment_loaded:
    sys.modules["Live"] = EmptyModule()  # type: ignore[assignment]
    sys.modules["MidiRemoteScript"] = EmptyModule()  # type: ignore[assignment]
    sys.modules["multipledispatch"] = EmptyModule()  # type: ignore[assignment]

from .Protocol0 import Protocol0  # noqa: E402

Protocol0.LIVE_ENVIRONMENT_LOADED = live_environment_loaded


def create_instance(c_instance):
    return Protocol0(c_instance)
