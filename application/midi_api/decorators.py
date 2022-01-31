from protocol0.my_types import Func, T

EXPOSED_P0_METHODS = {}


def api_exposable_class(cls):
    # type: (T) -> T
    for name, method in cls.__dict__.iteritems():
        if hasattr(method, "api_exposed"):
            EXPOSED_P0_METHODS[name] = cls
    return cls


def api_exposed(func):
    # type: (Func) -> Func
    func.api_exposed = True  # type: ignore
    return func
