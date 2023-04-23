from typing_extensions import Protocol, runtime_checkable


@runtime_checkable
class HasEmitter(Protocol):
    def target(self):
        # type: () -> object
        raise NotImplementedError
