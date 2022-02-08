import pytest

from protocol0.application.ErrorManager import ErrorManager
from protocol0.domain.shared.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.tests.fixtures.p0 import make_protocol0


def test_error_manager():
    make_protocol0()
    error_manager = ErrorManager()
    with pytest.raises(AssertionError):
        error_manager._handle_error_event(ErrorRaisedEvent("context"))
