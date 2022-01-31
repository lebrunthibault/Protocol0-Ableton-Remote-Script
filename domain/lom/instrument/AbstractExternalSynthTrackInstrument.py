from protocol0.domain.lom.instrument.AbstractInstrument import AbstractInstrument
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.routing.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.domain.lom.track.routing.InputRoutingTypeEnum import InputRoutingTypeEnum


class AbstractExternalSynthTrackInstrument(AbstractInstrument):
    MONOPHONIC = False
    RECORD_CLIP_TAILS = True
    HAS_PROTECTED_MODE = True
    EXTERNAL_INSTRUMENT_DEVICE = DeviceEnum.EXTERNAL_AUDIO_EFFECT
    MIDI_INPUT_ROUTING_TYPE = InputRoutingTypeEnum.REV2_AUX
    AUDIO_INPUT_ROUTING_CHANNEL = InputRoutingChannelEnum.POST_FX
    EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY = 0  # type: float

    def activate_editor_automation(self):
        # type: () -> None
        """ overridden by InstrumentProphet"""
        pass
