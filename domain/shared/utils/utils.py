import math
import pkgutil
import types

from typing import Optional, Any, Callable, Iterable

from protocol0.shared.Config import Config
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.types import T


def clamp(val, minv, maxv):
    # type: (float, float, float) -> float
    return max(minv, min(val, maxv))


def find_if(predicate, seq):
    # type: (Callable[[T], bool], Iterable[T]) -> Optional[T]
    for x in seq:
        if predicate(x):
            return x
    return None


def smart_string(s):
    # type: (Any) -> str
    if not isinstance(s, basestring):
        s = str(s)
    try:
        return s.decode("utf-8").encode("ascii", "ignore")
    except UnicodeEncodeError:
        return s.encode("utf-8")


def normalize_string(s):
    # type: (basestring) -> str
    return smart_string(s).strip().lower()


def import_package(package):
    # type: (types.ModuleType) -> None
    """ import all modules in a package """
    prefix = package.__name__ + "."
    for _, mod_name, _ in pkgutil.iter_modules(package.__path__, prefix):
        __import__(mod_name, fromlist="dummy")


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
