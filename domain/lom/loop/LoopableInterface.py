class LoopableInterface(object):
    @property
    def looping(self):
        # type: () -> bool
        raise NotImplementedError

    @looping.setter
    def looping(self, loop):
        # type: (bool) -> None
        raise NotImplementedError

    @property
    def start(self):
        # type: () -> float
        raise NotImplementedError

    @start.setter
    def start(self, start):
        # type: (float) -> None
        raise NotImplementedError

    @property
    def end(self):
        # type: () -> float
        raise NotImplementedError

    @end.setter
    def end(self, end):
        # type: (float) -> None
        raise NotImplementedError

    @property
    def length(self):
        # type: () -> float
        raise NotImplementedError

    @length.setter
    def length(self, length):
        # type: (float) -> None
        raise NotImplementedError
