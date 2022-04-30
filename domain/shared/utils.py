import inspect
import math
import pkgutil
import types
from collections import namedtuple
from types import FrameType

from qualname import qualname
from typing import Optional, Any, cast, Callable, List, Iterable

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Config import Config
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.types import T


def scroll_values(items, current_value, go_next, rotate=True):
    # type: (Iterable[T], Optional[T], bool, bool) -> T
    values = list(items)  # type: List[T]
    if len(values) == 0:
        raise Protocol0Warning("empty list handed to scroll_values")

    if current_value not in values:
        return values[0]

    increment = 1 if go_next else -1
    current_index = values.index(current_value)
    next_index = current_index + increment

    if rotate is False:
        next_index = int(clamp(next_index, 0, len(values) - 1))
    else:
        next_index = (current_index + increment) % len(values)

    return values[next_index]
    # try:
    #     return values[next_index]
    # except ValueError:
    #     return current_value


def clamp(val, minv, maxv):
    # type: (float, float, float) -> float
    return max(minv, min(val, maxv))


def find_if(predicate, seq):
    # type: (Callable[[T], bool], Iterable[T]) -> Optional[T]
    for x in seq:
        if predicate(x):
            return x
    return None


def get_frame_info(frame_count=1):
    # type: (int) -> Optional[Any]
    call_frame = inspect.currentframe()
    for _ in range(frame_count):
        next_frame = call_frame.f_back
        if not next_frame:
            break
        call_frame = next_frame
    try:
        (filename, line, method_name, _, _) = inspect.getframeinfo(cast(FrameType, call_frame))
    except IndexError:
        return None
    filename = filename.replace(Config.PROJECT_ROOT + "\\", "").replace(Config.REMOTE_SCRIPTS_ROOT + "\\", "")
    class_name = filename.replace(".py", "").split("\\")[-1]

    FrameInfo = namedtuple("FrameInfo", ["filename", "class_name", "line", "method_name"])
    return FrameInfo(filename=filename, class_name=class_name, line=line, method_name=method_name)


def is_method(func):
    # type: (Callable) -> bool
    spec = inspect.getargspec(func)
    return bool(spec.args and (spec.args[0] == "self" or spec.args[0] == "cls"))


def is_lambda(func):
    # type: (Callable) -> bool
    return isinstance(func, types.LambdaType) and func.__name__ == "<lambda>"


def smart_string(s):
    # type: (Any) -> str
    if not isinstance(s, basestring):
        s = str(s)
    try:
        return s.decode("utf-8").encode("ascii", "ignore")  # type: ignore
    except UnicodeEncodeError:
        return s.encode("utf-8")


def normalize_string(s):
    # type: (basestring) -> str
    return smart_string(s).strip().lower()


def get_inner_func(func):
    # type: (Any) -> Callable
    if hasattr(func, "function"):
        return get_inner_func(func.function)
    if hasattr(func, "func"):  # partial
        return get_inner_func(func.func)
    if hasattr(func, "original_func"):
        return get_inner_func(func.original_func)
    if hasattr(func, "listener"):
        return get_inner_func(func.listener)

    return func


def get_class_name_from_method(func):
    # type: (Any) -> str
    if hasattr(func, "__self__"):
        class_name = func.__self__.__class__.__name__
    elif hasattr(func, "__class__"):
        class_name = func.__class__.__name__
    else:
        raise Protocol0Error("Cannot get class_name from func")

    if class_name and all(word not in class_name for word in ["function", "None"]):
        return class_name

    try:
        return ".".join(qualname(func).split(".")[:-1])
    except (AttributeError, IOError):
        return "unknown %s" % func


def get_callable_repr(func):
    # type: (Any) -> str
    from protocol0.shared.sequence.Sequence import Sequence
    from protocol0.shared.sequence.SequenceStep import SequenceStep
    from protocol0.shared.sequence.CallbackDescriptor import CallableWithCallbacks
    if isinstance(func, Sequence) or isinstance(func, SequenceStep) or isinstance(func, CallableWithCallbacks):
        return func.__repr__()

    decorated_func = get_inner_func(func)
    class_name = get_class_name_from_method(decorated_func)

    if isinstance(decorated_func, CallableWithCallbacks):
        return decorated_func.__repr__()

    if not hasattr(decorated_func, "__name__"):
        return "only class_name %s" % class_name or "unknown"

    if class_name:
        return "%s.%s" % (class_name, decorated_func.__name__)
    else:
        return decorated_func.__name__


def import_package(package):
    # type: (types.ModuleType) -> None
    """ import all modules in a package """
    prefix = package.__name__ + "."
    for _, mod_name, _ in pkgutil.iter_modules(package.__path__, prefix):
        __import__(mod_name, fromlist="dummy")


def nop(*_, **__):
    # type: (Any, Any) -> None
    pass


def compare_values(value, expected_value):
    # type: (Any, Any) -> bool
    if isinstance(value, float):
        value = round(value, 3)
        expected_value = round(expected_value, 3)

    return value == expected_value


def get_length_legend(beat_length):
    # type: (float) -> str
    if int(beat_length) % SongFacade.signature_numerator() != 0:
        return "%d beat%s" % (beat_length, "s" if beat_length > 1 else "")
    else:
        bar_length = beat_length / SongFacade.signature_numerator()
        return "%d bar%s" % (bar_length, "s" if bar_length > 1 else "")


live_factor = 6 / math.log10(1.0 / Config.ZERO_VOLUME)


def volume_to_db(volume):
    # type: (float) -> float
    if volume == 0:
        return Config.ZERO_VOLUME_DB
    return live_factor * math.log10(round(volume, 3) / round(Config.ZERO_VOLUME, 3))


def db_to_volume(db):
    # type: (float) -> float
    return pow(10, db / live_factor) * Config.ZERO_VOLUME


class ForwardTo(object):
    # noinspection PyCallingNonCallable
    """
        A descriptor based recipe that makes it possible to write shorthands
        that forward attribute access from one object onto another.

        >>> class C(object):
        ...     def __init__(self):
        ...         class CC(object):
        ...             def xx(self, extra):
        ...                 return 100 + extra
        ...             foo = 42
        ...         self.cc = CC()
        ...
        ...     local_cc = ForwardTo('cc', 'xx')
        ...     local_foo = ForwardTo('cc', 'foo')
        ...
        >>> # noinspection PyCallingNonCallable
        >>> print C().local_cc(10)
        110
        >>> print C().local_foo
        42

        Arguments: objectName - name of the attribute containing the second object.
                   attrName - name of the attribute in the second object.
        Returns:   An object that will forward any calls as described above.
        """

    def __init__(self, object_name, attr_name):
        # type: (str, str) -> None
        self.object_name = object_name
        self.attr_name = attr_name

    def __get__(self, instance, _=None):
        # type: (object, Optional[object]) -> None
        return getattr(getattr(instance, self.object_name), self.attr_name)

    def __set__(self, instance, value):
        # type: (object, Any) -> None
        setattr(getattr(instance, self.object_name), self.attr_name, value)

    def __delete__(self, instance):
        # type: (object) -> None
        delattr(getattr(instance, self.object_name), self.attr_name)
