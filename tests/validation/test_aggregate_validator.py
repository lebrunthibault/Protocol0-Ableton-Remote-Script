from protocol0.validation.AggregateValidator import AggregateValidator
from protocol0.validation.CallbackValidator import CallbackValidator
from protocol0.validation.PropertyValidator import PropertyValidator


def test_callback_validator():
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
    validator = AggregateValidator([
        CallbackValidator(obj, lambda t: t.test == "test", lambda t: setattr(t, "test", "test")),
        PropertyValidator(obj, "test", "test")
    ])

    assert validator.is_valid()
    assert validator.get_error_message() is None

    validator = AggregateValidator([
        CallbackValidator(obj, lambda t: t.test == "toto", lambda t: setattr(t, "test", "toto")),
        PropertyValidator(obj, "test", "toto")
    ])

    assert not validator.is_valid()
    assert len(validator.get_error_message().split("\n")) == 2
    validator.fix()
    assert validator.is_valid()
