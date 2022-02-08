from protocol0 import EmptyModule
from protocol0.application.Protocol0 import Protocol0
from protocol0.tests.fixtures.song import AbletonSong


def make_protocol0():
    # type: () -> Protocol0
    Protocol0.song = lambda _: AbletonSong()
    return Protocol0(EmptyModule(name="c_instance", is_false=False))
