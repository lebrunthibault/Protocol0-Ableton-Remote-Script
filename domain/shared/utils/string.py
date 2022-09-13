from typing import Any


def smart_string(s):
    # type: (Any) -> str
    if not isinstance(s, basestring):
        s = str(s)
    try:
        return s.decode("utf-8").encode("ascii", "ignore")
    except UnicodeEncodeError:
        return s.encode("utf-8")


def title(s):
    # type: (str) -> str
    # .title is not good because of words starting with numbers
    return " ".join([word[0].capitalize() + word[1:] for word in s.split(" ")])


def to_pascal_case(s):
    # type: (str) -> str
    # .title is not good because of words starting with numbers
    return s.title().replace("_", " ")
