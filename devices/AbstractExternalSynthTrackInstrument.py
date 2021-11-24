from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.InputRoutingChannelEnum import InputRoutingChannelEnum


class AbstractExternalSynthTrackInstrument(AbstractInstrument):
    EXTERNAL_INSTRUMENT_DEVICE = DeviceEnum.EXTERNAL_AUDIO_EFFECT
    AUDIO_INPUT_ROUTING_CHANNEL = InputRoutingChannelEnum.POST_FX
    EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY = 0
