from typing import TypeVar, Callable, Any

T = TypeVar("T")
F = TypeVar("F", bound=Callable[..., Any])

StringOrNumber = TypeVar("StringOrNumber", str, float)
