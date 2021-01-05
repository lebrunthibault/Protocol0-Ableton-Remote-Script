import sys

sys.path.insert(0, "C:\Python27\Lib\site-packages")
sys.path.insert(0, "C:\Python27")
sys.path.insert(0, "C:\Python27\Lib")


class EmptyModule():
    def __init__(self, is_false=True):
        self.is_false = is_false

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
        return iter([(0, 0)])


# allows accessing code from this module from outside of the Live python environment, e.g. Jupyter tests
if "Live" not in sys.modules:
    sys.modules["Live"] = EmptyModule()
    sys.modules["MidiRemoteScript"] = EmptyModule()
    sys.modules["multipledispatch"] = EmptyModule()
    sys.path.insert(0, "C:\\Users\\thiba\\Google Drive\\music\\dev\\AbletonLive-API-Stub")

from .Protocol0 import Protocol0


def create_instance(c_instance):
    return Protocol0(c_instance)
