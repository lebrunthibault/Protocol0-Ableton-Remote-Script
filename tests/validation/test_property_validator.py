import pytest

from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.validation.PropertyValidator import PropertyValidator


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
    validator = PropertyValidator(obj, "test", "test")
    assert validator.is_valid()
    assert validator.get_error_message() is None

    validator = PropertyValidator(obj, "test", "toto")
    assert not validator.is_valid()
    assert validator.get_error_message() is not None
    validator.fix()
    assert validator.is_valid()

    validator = PropertyValidator(obj, "toto", "toto")
    assert not validator.is_valid()
    assert validator.get_error_message() is not None
    with pytest.raises(Protocol0Error):
        validator.fix()
