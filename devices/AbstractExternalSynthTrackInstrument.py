from typing import Optional

from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.InputRoutingChannelEnum import InputRoutingChannelEnum


class AbstractExternalSynthTrackInstrument(AbstractInstrument):
    EXTERNAL_INSTRUMENT_DEVICE = None  # type:  Optional[DeviceEnum]
    AUDIO_INPUT_ROUTING_CHANNEL = None  # type:  Optional[InputRoutingChannelEnum]
