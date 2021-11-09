from protocol0.enums.AbstractEnum import AbstractEnum


class InputRoutingChannelEnum(AbstractEnum):
    PRE_FX = "Pre FX"
    POST_FX = "Post FX"
    POST_MIXER = "Post Mixer"

    @property
    def label(self):
        # type: () -> str
        return self.value
