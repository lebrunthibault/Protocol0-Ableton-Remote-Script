from typing import List

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.device_parameter.DeviceParameterValue import DeviceParameterValue
from protocol0.shared.AbstractEnum import AbstractEnum
from protocol0.shared.Config import Config


class DeviceEnum(AbstractEnum):
    ADDICTIVE_KEYS = "ADDICTIVE_KEYS"
    ARPEGGIATOR_RACK = "ARPEGGIATOR_RACK"
    AUTO_FILTER_HIGH_PASS = "AUTO_FILTER_HIGH_PASS"
    AUTO_FILTER_LOW_PASS = "AUTO_FILTER_LOW_PASS"
    COMPRESSOR = "COMPRESSOR"
    DUMMY_RACK = "DUMMY_RACK"
    EQ_EIGHT = "EQ_EIGHT"
    EXTERNAL_AUDIO_EFFECT = "EXTERNAL_AUDIO_EFFECT"
    EXTERNAL_INSTRUMENT = "EXTERNAL_INSTRUMENT"
    LFO_TOOL = "LFO_TOOL"
    MINITAUR_EDITOR = "MINITAUR_EDITOR"
    MIX_RACK = "MIX_RACK"
    REV2_EDITOR = "REV2_EDITOR"
    SERUM = "SERUM"
    SIMPLER = "SIMPLER"
    SSL_COMP = "SSL_COMP"
    TRACK_SPACER = "TRACK_SPACER"
    TRUE_VERB = "TRUE_VERB"
    USAMO = "USAMO"
    UTILITY = "UTILITY"

    @property
    def device_name(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceEnum.ADDICTIVE_KEYS: "Addictive Keys",
            DeviceEnum.ARPEGGIATOR_RACK: "Arpeggiator rack",
            DeviceEnum.AUTO_FILTER_HIGH_PASS: "Auto Filter High Pass",
            DeviceEnum.AUTO_FILTER_LOW_PASS: "Auto Filter Low Pass",
            DeviceEnum.COMPRESSOR: "Compressor",
            DeviceEnum.DUMMY_RACK: "Dummy Rack",
            DeviceEnum.EQ_EIGHT: "EQ Eight",
            DeviceEnum.EXTERNAL_AUDIO_EFFECT: "Ext. Audio Effect",
            DeviceEnum.EXTERNAL_INSTRUMENT: "Ext. Instrument",
            DeviceEnum.LFO_TOOL: "LFOTool_x64",
            DeviceEnum.MINITAUR_EDITOR: "Minitaur Editor(x64)",
            DeviceEnum.MIX_RACK: "Mix Rack",
            DeviceEnum.REV2_EDITOR: "REV2Editor",
            DeviceEnum.SERUM: "Serum_x64",
            DeviceEnum.SIMPLER: "Simpler",
            DeviceEnum.SSL_COMP: "SSLComp Stereo",
            DeviceEnum.TRACK_SPACER: "Trackspacer 2.5",
            DeviceEnum.TRUE_VERB: "TrueVerb Stereo",
            DeviceEnum.USAMO: "usamo_x64",
            DeviceEnum.UTILITY: "Utility",
        })

    @property
    def browser_name(self):
        # type: () -> str
        return self.get_value_from_mapping({
            DeviceEnum.AUTO_FILTER_HIGH_PASS: "Auto Filter High Pass.adv",
            DeviceEnum.AUTO_FILTER_LOW_PASS: "Auto Filter Low Pass.adv",
            DeviceEnum.EXTERNAL_AUDIO_EFFECT: "External Audio Effect",
            DeviceEnum.EXTERNAL_INSTRUMENT: "External Instrument",
            DeviceEnum.COMPRESSOR: "Compressor",
            DeviceEnum.DUMMY_RACK: "Dummy Rack.adg",
            DeviceEnum.EQ_EIGHT: "EQ Eight",
            DeviceEnum.LFO_TOOL: "LFOTool.adg",
            DeviceEnum.MIX_RACK: "Mix Rack.adg",
            DeviceEnum.SIMPLER: "Simpler",
            DeviceEnum.SSL_COMP: "SSLComp Stereo",
            DeviceEnum.TRACK_SPACER: "Trackspacer 2.5",
            DeviceEnum.TRUE_VERB: "TrueVerb Stereo",
            DeviceEnum.UTILITY: "Utility",
        })

    @classmethod
    def favorites(cls):
        # type: () -> List[DeviceEnum]
        return [
            cls.COMPRESSOR,
            cls.EQ_EIGHT,
            cls.LFO_TOOL,
            cls.SSL_COMP,
            cls.TRACK_SPACER,
            cls.TRUE_VERB,
            cls.UTILITY,
        ]

    @property
    def is_user(self):
        # type: () -> bool
        return self in [
            DeviceEnum.AUTO_FILTER_HIGH_PASS,
            DeviceEnum.AUTO_FILTER_LOW_PASS,
            DeviceEnum.ARPEGGIATOR_RACK,
            DeviceEnum.DUMMY_RACK,
            DeviceEnum.MIX_RACK,
        ]

    @classmethod
    def updatable_devices(cls):
        # type: () -> List[DeviceEnum]
        return [cls.MIX_RACK, cls.LFO_TOOL]

    @classmethod
    def plugin_white_list(cls):
        # type: () -> List[DeviceEnum]
        return [
            cls.ADDICTIVE_KEYS,
            cls.REV2_EDITOR,
            cls.SERUM,
            cls.USAMO
        ]

    @classmethod
    def deprecated_devices(cls):
        # type: () -> List[DeviceEnum]
        return [cls.MINITAUR_EDITOR]

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
