from typing import Any


def smart_string(s):
    # type: (Any) -> str
    if not isinstance(s, basestring):
        s = str(s)
    try:
        return s.decode("utf-8").encode("ascii", "ignore")
    except UnicodeEncodeError:
        return s.encode("utf-8")
