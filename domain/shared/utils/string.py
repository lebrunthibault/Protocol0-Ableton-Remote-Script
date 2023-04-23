import sys

from typing import Any


def smart_string(s):
    # type: (Any) -> str
    if sys.version_info[0] == 3:
        return s

    if not isinstance(s, basestring):
        s = str(s)

    try:
        return s.decode("utf-8").encode("ascii", "ignore")
    except UnicodeEncodeError:
        return s.encode("utf-8")


def title(s):
    # type: (str) -> str
    # .title is not good because of words starting with numbers
    if not s:
        return s

    s = s.strip()

    return s[0].capitalize() + s[1:]
