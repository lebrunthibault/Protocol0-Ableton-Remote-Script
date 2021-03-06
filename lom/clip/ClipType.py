from a_protocol_0.utils.AbstractEnum import AbstractEnum


class ClipType(AbstractEnum):
    NORMAL = ""
    ONE_SHOT = "one"

    @classmethod
    def default(cls):
        return ClipType.NORMAL
