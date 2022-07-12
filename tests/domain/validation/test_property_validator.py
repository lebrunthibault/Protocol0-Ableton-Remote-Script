import pytest

from protocol0.domain.lom.validation.sub_validators.PropertyValueValidator import (
    PropertyValueValidator,
)
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error


def test_property_validator():
    class Test(object):
        def __init__(self):
            self._test = "test"

        @property
        def test(self):
            return self._test

        @test.setter
        def test(self, test):
            self._test = test

    obj = Test()
    validator = PropertyValueValidator(obj, "test", "test")
    assert validator.is_valid()
    assert validator.get_error_message() is None

    validator = PropertyValueValidator(obj, "test", "toto")
    assert not validator.is_valid()
    assert validator.get_error_message() is not None
    validator.fix()
    assert validator.is_valid()

    validator = PropertyValueValidator(obj, "toto", "toto")
    assert not validator.is_valid()
    assert validator.get_error_message() is not None
    with pytest.raises(Protocol0Error):
        validator.fix()
