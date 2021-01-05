import sys


class EmptyModule():
    def __init__(self, is_false=True):
        self.is_false = is_false

    def __ne__(self, other):
        return False

    def __eq__(self):
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
if "Live" not in sys.modules:
    sys.modules["Live"] = EmptyModule()
    sys.modules["MidiRemoteScript"] = EmptyModule()
    sys.modules["multipledispatch"] = EmptyModule()

from .Protocol0 import Protocol0


def create_instance(c_instance):
    return Protocol0(c_instance)
