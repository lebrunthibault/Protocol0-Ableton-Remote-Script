from typing import List, Optional, Union

from protocol0.domain.lom.device.DeviceEnumGroup import DeviceEnumGroup
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.device_parameter.DeviceParameterValue import DeviceParameterValue
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.AbstractEnum import AbstractEnum
from protocol0.shared.Config import Config


class DeviceEnum(AbstractEnum):
    ADDICTIVE_KEYS = "Addictive Keys"
    API_2500 = "API-2500 Stereo"
    AUDIO_EFFECT_RACK = "Audio Effect Rack"
    AUTO_FILTER = "Auto Filter"
    AUTO_FILTER_HIGH_PASS = "Auto Filter High Pass"
    AUTO_FILTER_LOW_PASS = "Auto Filter Low Pass"
    AUTO_PAN = "AutoPan"
    BEAT_REPEAT = "Beat Repeat"
    C1_COMP = "C1 comp Stereo"
    COMPRESSOR = "Compressor"
    DECAPITATOR = "Decapitator"
    DE_ESSER = "DeEsser Stereo"
    DELAY = "Delay"
    DRUM_BUSS = "Drum Buss"
    DOUBLER2 = "Doubler2 Stereo"
    DOUBLER4 = "Doubler4 Stereo"
    DRUM_RACK = "Drum Rack"
    EFFECTRIX = "Effectrix"
    ENIGMA = "Enigma Stereo"
    EQ_EIGHT = "EQ Eight"
    EQ_ROOM = "EQ Room"
    EXTERNAL_AUDIO_EFFECT = "Ext. Audio Effect"
    EXTERNAL_INSTRUMENT = "Ext. Instrument"
    FREE_CLIP = "FreeClip"
    GATE = "Gate"
    GATEKEEPER = "Gatekeeper"
    GLUE_COMPRESSOR = "Glue Compressor"
    H_COMP = "H-Comp Stereo"
    KONTAKT = "Kontakt 7"
    INSERT_DELAY = "Insert Delay"
    INSERT_DRY_WET = "Insert Dry Wet"
    INSERT_FILTER = "Insert Filter"
    INSERT_REVERB = "Insert Reverb"
    INSERT_VOLUME = "Insert Volume"
    INSTRUMENT_RACK = "Instrument Rack"
    JJP_STRINGS = "JJP-Strings-Keys Stereo"
    LFO_TOOL = "LFOTool_x64"
    L1_LIMITER = "L1 limiter Stereo"
    L1_ULTRAMAXIMIZER = "L1+ Ultramaximizer Stereo"
    LIMITER = "Limiter"
    MASTERING_RACK = "Mastering Rack"
    OPUS = "Opus"
    OZONE = "Ozone 9"
    PITCH = "Pitch"
    PLAY = "play_VST_x64"
    PRO_Q_3 = "Pro-Q 3"
    PRO_Q_3_VST3 = "FabFilter Pro-Q 3"
    REVERB = "Reverb"
    REV2_EDITOR = "REV2Editor"
    R_VERB = "RVerb Stereo"
    SAMPLE_PITCH_RACK = "Sample Pitch Rack"
    SATURATOR = "Saturator"
    SATURN_2 = "Saturn 2"
    SERUM = "Serum_x64"
    SIMPLER = "Simpler"
    SOOTHE2 = "soothe2"
    SOUNDID_REFERENCE_PLUGIN = "SoundID Reference Plugin"
    SPLICE = "Splice Bridge"
    SPIFF = "spiff"
    SSL_COMP = "SSLComp Stereo"
    SUPER_TAP_2 = "SuperTap 2-Taps Stereo"
    SUPER_TAP_6 = "SuperTap 6-Taps Stereo"
    SURFEREQ = "SurferEQ"
    SYLENTH1 = "Sylenth1"
    TRACK_SPACER = "Trackspacer 2.5"
    TRUE_VERB = "TrueVerb Stereo"
    TUNER = "Tuner"
    USAMO = "usamo_x64"
    UTILITY = "Utility"
    VALHALLA_VINTAGE_VERB = "ValhallaVintageVerb"
    VCOMP = "VComp Stereo"
    VEQ = "VEQ3 Stereo"
    YOULEAN = "Youlean Loudness Meter 2"

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
            DeviceEnum.MASTERING_RACK,
            DeviceEnum.SAMPLE_PITCH_RACK,
            DeviceEnum.INSERT_DELAY,
            DeviceEnum.INSERT_DRY_WET,
            DeviceEnum.INSERT_FILTER,
            DeviceEnum.INSERT_REVERB,
            DeviceEnum.INSERT_VOLUME,
        ]

    @property
    def is_external_device(self):
        # type: () -> bool
        return self.value in ("Ext. Audio Effect", "Ext. Instrument")

    @property
    def can_be_saved(self):
        # type: () -> bool
        return self not in [DeviceEnum.REV2_EDITOR, DeviceEnum.PLAY, DeviceEnum.OPUS]

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
                return "%s.adv" % self.value
            elif self.is_rack_preset:
                return "%s.adg" % self.value
            else:
                return self.value

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
            return self.value

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
                    DeviceEnum.AUTO_FILTER_HIGH_PASS: DeviceParameterEnum.AUTO_FILTER_HIGH_PASS_FREQUENCY,
                    DeviceEnum.AUTO_FILTER_LOW_PASS: DeviceParameterEnum.AUTO_FILTER_LOW_PASS_FREQUENCY,
                    DeviceEnum.AUTO_PAN: DeviceParameterEnum.AUTO_PAN_AMOUNT,
                    DeviceEnum.LIMITER: DeviceParameterEnum.LIMITER_GAIN,
                    DeviceEnum.LFO_TOOL: DeviceParameterEnum.LFO_TOOL_POINT_Y0,
                    DeviceEnum.SATURATOR: DeviceParameterEnum.SATURATOR_DRIVE,
                    DeviceEnum.UTILITY: DeviceParameterEnum.UTILITY_GAIN,
                }
            )
        except Protocol0Error:
            return None

    @classmethod
    def favorites(cls):
        # type: () -> List[List[Union[DeviceEnum, DeviceEnumGroup]]]
        return [
            [
                DeviceEnumGroup(
                    "Filter",
                    [cls.INSERT_FILTER, cls.AUTO_FILTER_HIGH_PASS, cls.AUTO_FILTER_LOW_PASS],
                ),
                DeviceEnumGroup("EQ", [cls.PRO_Q_3, cls.EQ_EIGHT, cls.VEQ]),
                cls.UTILITY,
            ],
            [
                DeviceEnumGroup(
                    "Comp", [cls.COMPRESSOR, cls.SSL_COMP, cls.H_COMP, cls.C1_COMP, cls.VCOMP]
                ),
                DeviceEnumGroup("Sat", [cls.SATURN_2, cls.SATURATOR, cls.DECAPITATOR]),
                # DeviceEnumGroup("Limiter", [cls.LIMITER, cls.L1_LIMITER, cls.L1_ULTRAMAXIMIZER]),
                cls.TRACK_SPACER,
            ],
            [
                DeviceEnumGroup("Volume", [cls.LFO_TOOL, cls.GATEKEEPER, cls.INSERT_VOLUME]),
                DeviceEnumGroup(
                    "Delay", [cls.INSERT_DELAY, cls.SUPER_TAP_6, cls.SUPER_TAP_2, cls.DELAY]
                ),
                DeviceEnumGroup(
                    "Reverb", [cls.INSERT_REVERB, cls.VALHALLA_VINTAGE_VERB, cls.TRUE_VERB]
                ),
            ],
            [
                cls.DRUM_RACK,
                cls.KONTAKT,
                cls.OPUS,
            ],
        ]

    @property
    def load_time(self):
        # type: () -> int
        """
        load time in ms : by how much loading a single device / plugin instance slows down the set startup
        measured by loading multiple device instances (20) in an empty set and timing multiple times the set load
        very rough approximation of the performance impact of a device on the whole set
        """
        try:
            return self.get_value_from_mapping(
                {
                    DeviceEnum.ADDICTIVE_KEYS: 1263,
                    DeviceEnum.API_2500: 95,
                    DeviceEnum.AUDIO_EFFECT_RACK: 8,
                    DeviceEnum.AUTO_FILTER: 7,
                    DeviceEnum.BEAT_REPEAT: 7,
                    DeviceEnum.COMPRESSOR: 11,
                    DeviceEnum.DECAPITATOR: 309,
                    DeviceEnum.DE_ESSER: 90,
                    DeviceEnum.DELAY: 10,
                    DeviceEnum.DRUM_BUSS: 18,
                    DeviceEnum.DOUBLER2: 43,
                    DeviceEnum.DOUBLER4: 46,
                    DeviceEnum.EFFECTRIX: 133,
                    DeviceEnum.ENIGMA: 0,
                    DeviceEnum.EQ_EIGHT: 31,
                    DeviceEnum.EQ_ROOM: 31,
                    DeviceEnum.EXTERNAL_AUDIO_EFFECT: 5,
                    DeviceEnum.EXTERNAL_INSTRUMENT: 20,
                    DeviceEnum.FREE_CLIP: 40,
                    DeviceEnum.KONTAKT: 1000,
                    DeviceEnum.GATE: 7,
                    DeviceEnum.GATEKEEPER: 130,
                    DeviceEnum.GLUE_COMPRESSOR: 6,
                    DeviceEnum.H_COMP: 75,
                    DeviceEnum.INSTRUMENT_RACK: 10,
                    DeviceEnum.JJP_STRINGS: 280,
                    DeviceEnum.LFO_TOOL: 180,
                    DeviceEnum.L1_LIMITER: 64,
                    DeviceEnum.L1_ULTRAMAXIMIZER: 64,
                    DeviceEnum.LIMITER: 5,
                    DeviceEnum.PITCH: 2,
                    DeviceEnum.PLAY: 214,
                    DeviceEnum.PRO_Q_3: 53,
                    DeviceEnum.PRO_Q_3_VST3: 53,
                    DeviceEnum.REVERB: 9,
                    DeviceEnum.REV2_EDITOR: 80,
                    DeviceEnum.R_VERB: 114,
                    DeviceEnum.SATURATOR: 8,
                    DeviceEnum.SATURN_2: 50,
                    DeviceEnum.SERUM: 147,
                    DeviceEnum.SIMPLER: 56,
                    DeviceEnum.SOOTHE2: 206,
                    DeviceEnum.SOUNDID_REFERENCE_PLUGIN: 0,
                    DeviceEnum.SPIFF: 270,
                    DeviceEnum.SSL_COMP: 81,
                    DeviceEnum.SUPER_TAP_2: 45,
                    DeviceEnum.SUPER_TAP_6: 45,
                    DeviceEnum.SURFEREQ: 116,
                    DeviceEnum.SYLENTH1: 314,
                    DeviceEnum.TRACK_SPACER: 207,
                    DeviceEnum.TRUE_VERB: 82,
                    DeviceEnum.TUNER: 0,
                    DeviceEnum.USAMO: 78,
                    DeviceEnum.UTILITY: 4,
                    DeviceEnum.VALHALLA_VINTAGE_VERB: 71,
                    DeviceEnum.VCOMP: 52,
                    DeviceEnum.VEQ: 55,
                }
            )
        except Protocol0Error:
            return 0

    @property
    def is_instrument(self):
        # type: () -> bool
        return self in [
            DeviceEnum.REV2_EDITOR,
            DeviceEnum.KONTAKT,
            DeviceEnum.OPUS,
            DeviceEnum.PLAY,
            DeviceEnum.DRUM_RACK,
            DeviceEnum.SPLICE,
        ]

    @classmethod
    def missing_plugin_names(cls):
        # type: () -> List[str]
        """Plugins that I've used, but I don't currently have (formerly cracks)"""
        return ["Vocal Rider Stereo", "API-2500 Stereo", DeviceEnum.SATURN_2.value]
