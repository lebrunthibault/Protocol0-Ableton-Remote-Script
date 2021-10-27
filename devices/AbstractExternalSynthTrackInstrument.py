from typing import Optional

from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.DeviceNameEnum import DeviceNameEnum
from protocol0.enums.InputRoutingChannelEnum import InputRoutingChannelEnum


class AbstractExternalSynthTrackInstrument(AbstractInstrument):
    EXTERNAL_INSTRUMENT_DEVICE = None  # type:  Optional[DeviceNameEnum]
    AUDIO_INPUT_ROUTING_CHANNEL = None  # type:  Optional[InputRoutingChannelEnum]
