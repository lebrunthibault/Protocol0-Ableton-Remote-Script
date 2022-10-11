import pkgutil
import types

from typing import Any, List

from protocol0.shared.Config import Config


def clamp(val, min_v, max_v):
    # type: (float, float, float) -> float
    return max(min_v, min(val, max_v))


def import_package(package):
    # type: (types.ModuleType) -> None
    """import all modules in a package"""
    prefix = package.__name__ + "."
    for _, mod_name, _ in pkgutil.iter_modules(package.__path__, prefix):
        __import__(mod_name, fromlist="dummy")


def compare_values(value, expected_value):
    # type: (Any, Any) -> bool
    if isinstance(value, float):
        value = round(value, 3)
        expected_value = round(expected_value, 3)

    return value == expected_value


def get_length_legend(beat_length, signature_numerator):
    # type: (float, int) -> str
    if int(beat_length) % signature_numerator != 0:
        return "%d beat%s" % (beat_length, "s" if beat_length > 1 else "")
    else:
        bar_length = beat_length / signature_numerator
        return "%d bar%s" % (bar_length, "s" if bar_length > 1 else "")


def get_minutes_legend(seconds):
    # type: (float) -> str
    minutes = int(seconds / 60)
    seconds = int(seconds % 60)

    return "%02d:%02d" % (minutes, seconds)


def volume_to_db(vol):
    # type: (float) -> float
    if round(vol, 3) == round(Config.ZERO_VOLUME, 3):
        return 0

    return polynomial(
        vol, [3593.2, -18265.9, 39231, -45962.3, 31461.7, -12322.4, 2371.63, -39.9082, -60.9928]
    )


def db_to_volume(db):
    # type: (float) -> float
    if db == 0:
        return Config.ZERO_VOLUME

    if db < -60:
        return 0

    return polynomial(
        db,
        [
            -1.419398502456 * pow(10, -10),
            -1.8321104871497 * pow(10, -8),
            -7.93316011830 * pow(10, -7),
            -0.0000133509,
            -0.0000590049,
            0.000480888,
            0.0282999,
            0.85,
        ],
    )


def polynomial(x, coeffs):
    # type: (float, List[float]) -> float
    """Using polynomial interpolation"""
    coeffs = list(reversed(coeffs))

    def make_term(val, index):
        # type: (float, int) -> float
        term = coeffs[index]
        if index > 0:
            term *= pow(val, index)
        return term

    return sum([make_term(x, i) for i in range(len(coeffs))])
