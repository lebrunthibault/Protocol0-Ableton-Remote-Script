import pytest

from protocol0.application.ErrorService import ErrorService
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.tests.domain.fixtures.p0 import make_protocol0


def test_error_service():
    make_protocol0()
    error_manager = ErrorService()
    with pytest.raises(AssertionError):
        error_manager._on_error_raised_event(ErrorRaisedEvent("context"))
