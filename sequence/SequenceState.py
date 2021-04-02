from a_protocol_0.enums.AbstractEnum import AbstractEnum


class SequenceState(AbstractEnum):
    UN_STARTED = "UN_STARTED"
    STARTED = "STARTED"
    TERMINATED = "TERMINATED"
    ERRORED = "ERRORED"


class SequenceLogLevel:
    DISABLED = 1
    INFO = 2
    DEBUG = 3
