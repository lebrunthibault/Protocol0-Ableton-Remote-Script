from typing import List

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.device_parameter.DeviceParameterValue import DeviceParameterValue
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.AbstractEnum import AbstractEnum
from protocol0.shared.Config import Config


class DeviceEnum(AbstractEnum):
    ADDICTIVE_KEYS = "ADDICTIVE_KEYS"
    API_2500 = "API_2500"
    ARPEGGIATOR_RACK = "ARPEGGIATOR_RACK"
    AUTO_FILTER_HIGH_PASS = "AUTO_FILTER_HIGH_PASS"
    AUTO_FILTER_LOW_PASS = "AUTO_FILTER_LOW_PASS"
    COMPRESSOR = "COMPRESSOR"
    DRUM_RACK = "DRUM_RACK"
    DUMMY_RACK = "DUMMY_RACK"
    EQ_EIGHT = "EQ_EIGHT"
    EQ_EIGHT_RACK = "EQ_EIGHT_RACK"
    EQ_ROOM = "EQ_ROOM"
    EXTERNAL_AUDIO_EFFECT = "EXTERNAL_AUDIO_EFFECT"
    EXTERNAL_INSTRUMENT = "EXTERNAL_INSTRUMENT"
    LFO_TOOL = "LFO_TOOL"
    MINITAUR_EDITOR = "MINITAUR_EDITOR"
    MIX_RACK = "MIX_RACK"
    PRO_Q_3 = "PRO_Q_3"
    REV2_EDITOR = "REV2_EDITOR"
    SATURATOR = "SATURATOR"
    SATURN_2 = "SATURN_2"
    SERUM = "SERUM"
    SIMPLER = "SIMPLER"
    SSL_COMP = "SSL_COMP"
    TRACK_SPACER = "TRACK_SPACER"
    TRUE_VERB = "TRUE_VERB"
    TUNER = "TUNER"
    USAMO = "USAMO"
    UTILITY = "UTILITY"

    @property
    def device_name(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceEnum.ADDICTIVE_KEYS: "Addictive Keys",
            DeviceEnum.API_2500: "API-2500 Stereo",
            DeviceEnum.ARPEGGIATOR_RACK: "Arpeggiator rack",
            DeviceEnum.AUTO_FILTER_HIGH_PASS: "Auto Filter High Pass",
            DeviceEnum.AUTO_FILTER_LOW_PASS: "Auto Filter Low Pass",
            DeviceEnum.COMPRESSOR: "Compressor",
            DeviceEnum.DRUM_RACK: "Drum Rack",
            DeviceEnum.DUMMY_RACK: "Dummy Rack",
            DeviceEnum.EQ_EIGHT: "EQ Eight",
            DeviceEnum.EQ_EIGHT_RACK: "EQ Eight Rack",
            DeviceEnum.EQ_ROOM: "EQ Room",
            DeviceEnum.EXTERNAL_AUDIO_EFFECT: "Ext. Audio Effect",
            DeviceEnum.EXTERNAL_INSTRUMENT: "Ext. Instrument",
            DeviceEnum.LFO_TOOL: "LFOTool_x64",
            DeviceEnum.MINITAUR_EDITOR: "Minitaur Editor(x64)",
            DeviceEnum.MIX_RACK: "Mix Rack",
            DeviceEnum.PRO_Q_3: "FabFilter Pro-Q 3",
            DeviceEnum.REV2_EDITOR: "REV2Editor",
            DeviceEnum.SATURATOR: "Saturator",
            DeviceEnum.SATURN_2: "FabFilter Saturn 2",
            DeviceEnum.SERUM: "Serum_x64",
            DeviceEnum.SIMPLER: "Simpler",
            DeviceEnum.SSL_COMP: "SSLComp Stereo",
            DeviceEnum.TRACK_SPACER: "Trackspacer 2.5",
            DeviceEnum.TRUE_VERB: "TrueVerb Stereo",
            DeviceEnum.TUNER: "Tuner",
            DeviceEnum.USAMO: "usamo_x64",
            DeviceEnum.UTILITY: "Utility",
        })

    @property
    def browser_name(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceEnum.API_2500: "API-2500 Stereo",
            DeviceEnum.ARPEGGIATOR_RACK: "Arpeggiator rack.adg",
            DeviceEnum.AUTO_FILTER_HIGH_PASS: "Auto Filter High Pass.adv",
            DeviceEnum.AUTO_FILTER_LOW_PASS: "Auto Filter Low Pass.adv",
            DeviceEnum.EXTERNAL_AUDIO_EFFECT: "External Audio Effect",
            DeviceEnum.EXTERNAL_INSTRUMENT: "External Instrument",
            DeviceEnum.COMPRESSOR: "Compressor",
            DeviceEnum.DRUM_RACK: "Drum Rack",
            DeviceEnum.DUMMY_RACK: "Dummy Rack.adg",
            DeviceEnum.EQ_EIGHT: "EQ Eight",
            DeviceEnum.EQ_EIGHT_RACK: "EQ Eight Rack.adg",
            DeviceEnum.EQ_ROOM: "EQ Room.adv",
            DeviceEnum.LFO_TOOL: "LFOTool_x64",
            DeviceEnum.MIX_RACK: "Mix Rack.adg",
            DeviceEnum.PRO_Q_3: "FabFilter Pro-Q 3",
            DeviceEnum.SATURATOR: "Saturator",
            DeviceEnum.SATURN_2: "FabFilter Saturn 2",
            DeviceEnum.SIMPLER: "Simpler",
            DeviceEnum.SSL_COMP: "SSLComp Stereo",
            DeviceEnum.TRACK_SPACER: "Trackspacer 2.5",
            DeviceEnum.TRUE_VERB: "TrueVerb Stereo",
            DeviceEnum.TUNER: "Tuner",
            DeviceEnum.UTILITY: "Utility",
        })

    @classmethod
    def favorites(cls):
        # type: () -> List[List[DeviceEnum]]
        return [
            [
                cls.EQ_EIGHT,
                cls.PRO_Q_3,
                cls.UTILITY,
                cls.COMPRESSOR,
                cls.SSL_COMP,
                cls.API_2500,
            ],
            [
                cls.SATURATOR,
                cls.SATURN_2,
                cls.TRUE_VERB,

            ],
            [
                cls.TRACK_SPACER,
                cls.LFO_TOOL,
                cls.TUNER,
            ]
        ]

    @classmethod
    def updatable_devices(cls):
        # type: () -> List[DeviceEnum]
        return [cls.MIX_RACK, cls.LFO_TOOL]

    @property
    def main_parameters_default(self):
        # type: () -> List[DeviceParameterValue]
        return self.get_value_from_mapping({
            DeviceEnum.ARPEGGIATOR_RACK: [DeviceParameterValue(DeviceParameterEnum.CHAIN_SELECTOR, 0)],
            DeviceEnum.COMPRESSOR: [
                DeviceParameterValue(DeviceParameterEnum.COMPRESSOR_OUTPUT_GAIN, 0),
                DeviceParameterValue(DeviceParameterEnum.COMPRESSOR_THRESHOLD, Config.ZERO_VOLUME),  # 0db
            ],
            DeviceEnum.EQ_EIGHT: [
                DeviceParameterValue(DeviceParameterEnum.EQ_EIGHT_FREQUENCY_1_A, 0.285494267941),
                DeviceParameterValue(DeviceParameterEnum.EQ_EIGHT_GAIN_4_A, 0),
                DeviceParameterValue(DeviceParameterEnum.EQ_EIGHT_FREQUENCY_8_A, 1),
            ],  # 90 Hz
            DeviceEnum.LFO_TOOL: [DeviceParameterValue(DeviceParameterEnum.LFO_TOOL_LFO_DEPTH, 0)],
            DeviceEnum.UTILITY: [
                DeviceParameterValue(DeviceParameterEnum.UTILITY_GAIN, 0),
                DeviceParameterValue(DeviceParameterEnum.UTILITY_MID_SIDE, 1)
            ],
        })

    def matches_device(self, device):
        # type: (Device) -> bool
        return device.name == self.device_name

    @classmethod
    def from_device_parameter(cls, device_parameter_enum):
        # type: (DeviceParameterEnum) -> DeviceEnum
        mapping = ({
            DeviceParameterEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: DeviceEnum.AUTO_FILTER_HIGH_PASS,
            DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: DeviceEnum.AUTO_FILTER_LOW_PASS,
            DeviceParameterEnum.UTILITY_GAIN: DeviceEnum.UTILITY,
        })

        if device_parameter_enum not in mapping:
            raise Protocol0Error("parameter not in mapping")

        return mapping[device_parameter_enum]
