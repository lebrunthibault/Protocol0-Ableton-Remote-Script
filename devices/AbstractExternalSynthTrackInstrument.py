from protocol0.devices.AbstractInstrument import AbstractInstrument
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.enums.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.sequence.Sequence import Sequence


class AbstractExternalSynthTrackInstrument(AbstractInstrument):
    MONOPHONIC = False
    RECORD_CLIP_TAILS = True
    HAS_PROTECTED_MODE = True
    EXTERNAL_INSTRUMENT_DEVICE = DeviceEnum.EXTERNAL_AUDIO_EFFECT
    MIDI_INPUT_ROUTING_TYPE = InputRoutingTypeEnum.ALL_INS
    AUDIO_INPUT_ROUTING_CHANNEL = InputRoutingChannelEnum.POST_FX
    EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY = 0  # type: float

    def activate_editor_automation(self):
        # type: () -> Sequence()
        """ overridden by InstrumentProphet"""
        pass
