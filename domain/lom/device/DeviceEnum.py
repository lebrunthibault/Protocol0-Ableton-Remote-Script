from typing import List, Optional

from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.device_parameter.DeviceParameterValue import DeviceParameterValue
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.string import to_pascal_case
from protocol0.shared.AbstractEnum import AbstractEnum
from protocol0.shared.Config import Config


class DeviceEnum(AbstractEnum):
    ADDICTIVE_KEYS = "ADDICTIVE_KEYS"
    API_2500 = "API_2500"
    AUDIO_EFFECT_RACK = "AUDIO_EFFECT_RACK"
    AUTO_FILTER = "AUTO_FILTER"
    AUTO_FILTER_HIGH_PASS = "AUTO_FILTER_HIGH_PASS"
    AUTO_FILTER_LOW_PASS = "AUTO_FILTER_LOW_PASS"
    AUTO_PAN = "AUTO_PAN"
    BEAT_REPEAT = "BEAT_REPEAT"
    COMPRESSOR = "COMPRESSOR"
    DELAY = "DELAY"
    DRUM_RACK = "DRUM_RACK"
    EFFECTRIX = "EFFECTRIX"
    EQ_EIGHT = "EQ_EIGHT"
    EQ_ROOM = "EQ_ROOM"
    EXTERNAL_AUDIO_EFFECT = "EXTERNAL_AUDIO_EFFECT"
    EXTERNAL_INSTRUMENT = "EXTERNAL_INSTRUMENT"
    FREE_CLIP = "FREE_CLIP"
    GATE = "GATE"
    GLUE_COMPRESSOR = "GLUE_COMPRESSOR"
    INSERT_DELAY = "INSERT_DELAY"
    INSERT_REVERB = "INSERT_REVERB"
    INSTRUMENT_RACK = "INSTRUMENT_RACK"
    LFO_TOOL = "LFO_TOOL"
    LIMITER = "LIMITER"
    PITCH = "PITCH"
    PRO_Q_3 = "PRO_Q_3"
    REVERB = "REVERB"
    REV2_EDITOR = "REV2_EDITOR"
    SAMPLE_PITCH_RACK = "SAMPLE_PITCH_RACK"
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
    VALHALLA_VINTAGE_VERB = "VALHALLA_VINTAGE_VERB"

    @property
    def device_name(self):
        # type: () -> str
        try:
            return self.get_value_from_mapping(
                {
                    DeviceEnum.API_2500: "API-2500 Stereo",
                    DeviceEnum.EQ_EIGHT: "EQ Eight",
                    DeviceEnum.EQ_ROOM: "EQ Room",
                    DeviceEnum.EXTERNAL_AUDIO_EFFECT: "Ext. Audio Effect",
                    DeviceEnum.EXTERNAL_INSTRUMENT: "Ext. Instrument",
                    DeviceEnum.FREE_CLIP: "FreeClip",
                    DeviceEnum.LFO_TOOL: "LFOTool_x64",
                    DeviceEnum.PRO_Q_3: "Pro-Q 3",
                    DeviceEnum.REV2_EDITOR: "REV2Editor",
                    DeviceEnum.SATURN_2: "Saturn 2",
                    DeviceEnum.SERUM: "Serum_x64",
                    DeviceEnum.SSL_COMP: "SSLComp Stereo",
                    DeviceEnum.TRACK_SPACER: "Trackspacer 2.5",
                    DeviceEnum.TRUE_VERB: "TrueVerb Stereo",
                    DeviceEnum.USAMO: "usamo_x64",
                    DeviceEnum.VALHALLA_VINTAGE_VERB: "ValhallaVintageVerb",
                }
            )
        except Protocol0Error:
            return to_pascal_case(self.name)

    @property
    def is_device_preset(self):
        # type: () -> bool
        return self in [
            DeviceEnum.AUTO_FILTER_HIGH_PASS,
            DeviceEnum.AUTO_FILTER_LOW_PASS,
            DeviceEnum.EQ_ROOM,
        ]

    @property
    def is_rack_preset(self):
        # type: () -> bool
        return self in [
            DeviceEnum.SAMPLE_PITCH_RACK,
            DeviceEnum.INSERT_DELAY,
            DeviceEnum.INSERT_REVERB,
        ]

    @property
    def browser_name(self):
        # type: () -> str
        try:
            return self.get_value_from_mapping(
                {
                    DeviceEnum.EXTERNAL_AUDIO_EFFECT: "External Audio Effect",
                    DeviceEnum.EXTERNAL_INSTRUMENT: "External Instrument",
                }
            )
        except Protocol0Error:
            if self.is_device_preset:
                return "%s.adv" % self.device_name
            elif self.is_rack_preset:
                return "%s.adg" % self.device_name
            else:
                return self.device_name

    @property
    def class_name(self):
        # type: () -> str
        try:
            return self.get_value_from_mapping(
                {
                    DeviceEnum.AUDIO_EFFECT_RACK: "AudioEffectGroupDevice",
                    DeviceEnum.AUTO_FILTER: "AutoFilter",
                    DeviceEnum.EQ_EIGHT: "Eq8",
                    DeviceEnum.EXTERNAL_AUDIO_EFFECT: "ProxyAudioEffectDevice",
                    DeviceEnum.EXTERNAL_INSTRUMENT: "ProxyInstrumentDevice",
                    DeviceEnum.INSTRUMENT_RACK: "InstrumentGroupDevice",
                    DeviceEnum.PITCH: "MidiPitcher",
                }
            )
        except Protocol0Error:
            return self.device_name

    @property
    def main_parameters_default(self):
        # type: () -> List[DeviceParameterValue]
        return self.get_value_from_mapping(
            {
                DeviceEnum.COMPRESSOR: [
                    DeviceParameterValue(DeviceParameterEnum.COMPRESSOR_OUTPUT_GAIN, 0),
                    DeviceParameterValue(
                        DeviceParameterEnum.COMPRESSOR_THRESHOLD, Config.ZERO_VOLUME
                    ),  # 0db
                ],
                DeviceEnum.EQ_EIGHT: [
                    DeviceParameterValue(
                        DeviceParameterEnum.EQ_EIGHT_FREQUENCY_1_A, 0.285494267941
                    ),
                    DeviceParameterValue(DeviceParameterEnum.EQ_EIGHT_GAIN_4_A, 0),
                    DeviceParameterValue(DeviceParameterEnum.EQ_EIGHT_FREQUENCY_8_A, 1),
                ],  # 90 Hz
                DeviceEnum.LFO_TOOL: [
                    DeviceParameterValue(DeviceParameterEnum.LFO_TOOL_LFO_DEPTH, 0),
                ],
                DeviceEnum.UTILITY: [
                    DeviceParameterValue(DeviceParameterEnum.UTILITY_GAIN, 0),
                    DeviceParameterValue(DeviceParameterEnum.UTILITY_MID_SIDE, 1),
                ],
            }
        )

    @property
    def default_parameter(self):
        # type: () -> Optional[DeviceParameterEnum]
        """Represents the main parameter for a specific device. We want to make it easily accessible"""
        try:
            return self.get_value_from_mapping(
                {
                    DeviceEnum.UTILITY: DeviceParameterEnum.UTILITY_GAIN,
                    DeviceEnum.AUTO_FILTER_LOW_PASS: DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY,
                    DeviceEnum.LIMITER: DeviceParameterEnum.LIMITER_GAIN,
                    DeviceEnum.SATURATOR: DeviceParameterEnum.SATURATOR_DRIVE,
                    DeviceEnum.AUTO_PAN: DeviceParameterEnum.AUTO_PAN_AMOUNT,
                }
            )
        except Protocol0Error:
            return None

    @classmethod
    def from_device_parameter(cls, device_parameter_enum):
        # type: (DeviceParameterEnum) -> DeviceEnum
        mapping = {
            DeviceParameterEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY: DeviceEnum.AUTO_FILTER_HIGH_PASS,
            DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY: DeviceEnum.AUTO_FILTER_LOW_PASS,
            DeviceParameterEnum.UTILITY_GAIN: DeviceEnum.UTILITY,
        }

        if device_parameter_enum not in mapping:
            raise Protocol0Error("parameter not in mapping")

        return mapping[device_parameter_enum]

    @classmethod
    def favorites(cls):
        # type: () -> List[List[DeviceEnum]]
        return [
            [
                cls.EQ_EIGHT,
                cls.AUTO_FILTER_LOW_PASS,
                cls.PRO_Q_3,
                cls.UTILITY,
            ],
            [
                cls.COMPRESSOR,
                cls.SSL_COMP,
                cls.LIMITER,
                cls.FREE_CLIP,
            ],
            [
                cls.SATURATOR,
                cls.SATURN_2,
                cls.AUTO_PAN,
            ],
            [cls.REV2_EDITOR],
        ]

    @classmethod
    def insert_favorites(cls):
        # type: () -> List[DeviceEnum]
        return [cls.INSERT_DELAY, cls.INSERT_REVERB]

    @property
    def load_time(self):
        # type: () -> int
        """
        load time in ms : by how much loading a single device / plugin instance slows down the set startup
        measured by loading multiple device instances (20) in an empty set and timing multiple times the set load
        very rough approximation of the performance impact of a device on the whole set
        """
        return self.get_value_from_mapping(
            {
                DeviceEnum.ADDICTIVE_KEYS: 1263,
                DeviceEnum.API_2500: 95,
                DeviceEnum.AUDIO_EFFECT_RACK: 8,
                DeviceEnum.AUTO_FILTER: 7,
                DeviceEnum.BEAT_REPEAT: 7,
                DeviceEnum.COMPRESSOR: 11,
                DeviceEnum.DELAY: 10,
                DeviceEnum.EFFECTRIX: 133,
                DeviceEnum.EQ_EIGHT: 31,
                DeviceEnum.EQ_ROOM: 31,
                DeviceEnum.EXTERNAL_AUDIO_EFFECT: 5,
                DeviceEnum.EXTERNAL_INSTRUMENT: 20,
                DeviceEnum.FREE_CLIP: 40,
                DeviceEnum.GATE: 7,
                DeviceEnum.GLUE_COMPRESSOR: 6,
                DeviceEnum.INSTRUMENT_RACK: 10,
                DeviceEnum.LFO_TOOL: 180,
                DeviceEnum.LIMITER: 5,
                DeviceEnum.PITCH: 2,
                DeviceEnum.PRO_Q_3: 53,
                DeviceEnum.REVERB: 9,
                DeviceEnum.REV2_EDITOR: 80,
                DeviceEnum.SATURATOR: 8,
                DeviceEnum.SATURN_2: 50,
                DeviceEnum.SERUM: 147,
                DeviceEnum.SIMPLER: 56,
                DeviceEnum.SSL_COMP: 81,
                DeviceEnum.TRACK_SPACER: 207,
                DeviceEnum.TRUE_VERB: 82,
                DeviceEnum.TUNER: 0,
                DeviceEnum.USAMO: 78,
                DeviceEnum.UTILITY: 4,
                DeviceEnum.VALHALLA_VINTAGE_VERB: 71,
            }
        )

    @classmethod
    def missing_plugin_names(cls):
        # type: () -> List[str]
        """Plugins that I've used, but I don't currently have (formerly cracks)"""
        return ["Vocal Rider Stereo", "API-2500 Stereo", DeviceEnum.SATURN_2.device_name]
