from protocol0.enums.AbstractEnum import AbstractEnum


class InputRoutingChannelEnum(AbstractEnum):
    # AUDIO
    PRE_FX = "Pre FX"
    POST_FX = "Post FX"
    POST_MIXER = "Post Mixer"

    # MIDI
    CHANNEL_1 = "Ch. 1"

    @property
    def label(self):
        # type: () -> str
        return self.value
