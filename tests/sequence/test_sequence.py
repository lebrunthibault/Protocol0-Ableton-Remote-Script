from __future__ import print_function
import pytest
from a_protocol_0.sequence.Sequence import Sequence
from a_protocol_0.sequence.SequenceError import SequenceError
from a_protocol_0.sequence.SequenceState import SequenceState
from a_protocol_0.tests.test_all import p0
from a_protocol_0.utils.decorators import has_callback_queue
from a_protocol_0.utils.log import log_ableton


# def test_sanity_checks():
#     with p0.component_guard():
#         seq = Sequence()
#         seq.done()
#         assert seq._state == SequenceState.TERMINATED
#
#         with pytest.raises(SequenceError):
#             seq.add(wait=3)
#
#         with pytest.raises(SequenceError):
#             Sequence().done().done()
#

# def test_simple_timeout():
#     with p0.component_guard():
#         seq = Sequence()
#         seq.add(lambda: log_ableton("execution"), complete_on=lambda: False, name="timeout step", check_timeout=0)
#         seq.add(lambda: log_ableton("unreachable step"), name="unreachable step")
#         seq.done()
#
#         assert seq._state == SequenceState.TERMINATED
#         assert seq._errored

#
# def test_callback_timeout():
#     class Example:
#         @has_callback_queue
#         def listener(self):
#             print("listener call")
#
#     obj = Example()
#
#     with p0.component_guard():
#         seq = Sequence()
#         seq.add(lambda: log_ableton("execution"), complete_on=obj.listener, name="timeout step", check_timeout=0)
#         seq.add(lambda: log_ableton("unreachable step"), name="unreachable step")
#         seq.done()
#
#         assert seq._state == SequenceState.TERMINATED
#         assert seq._errored
#
#     with p0.component_guard():
#         seq = Sequence()
#         seq.add(lambda: log_ableton("execution"), complete_on=obj.listener, name="timeout step", check_timeout=1)
#         seq.add(lambda: log_ableton("unreachable step"), name="unreachable step")
#         seq.done()
#         obj.listener()
#
#         assert seq._state == SequenceState.TERMINATED
#         assert not seq._errored


def test_async_callback_timeout():
    class Example:
        @has_callback_queue
        def listener(self):
            print("listener call")
            seq = Sequence()
            seq.add(wait=1)
            seq.add(lambda: print("after wait"))
            seq.done()

    obj = Example()

    with p0.component_guard():
        seq = Sequence()
        seq.add(lambda: log_ableton("execution"), complete_on=obj.listener, name="timeout step", check_timeout=2)
        seq.add(lambda: log_ableton("after listener step"), name="after listener step")
        seq.done()
        obj.listener()

        assert seq._state == SequenceState.TERMINATED
        assert not seq._errored
