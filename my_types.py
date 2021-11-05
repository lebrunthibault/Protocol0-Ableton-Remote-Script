from typing import TypeVar, Callable, Any

T = TypeVar("T")

StringOrNumber = TypeVar("StringOrNumber", str, float, int)
Func = Callable[..., Any]
