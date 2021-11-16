from typing import cast

from protocol0.devices.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.enums.ColorEnum import ColorEnum
from protocol0.enums.DeviceEnum import DeviceEnum
from protocol0.enums.InputRoutingChannelEnum import InputRoutingChannelEnum
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.sequence.Sequence import Sequence


class InstrumentMinitaur(AbstractExternalSynthTrackInstrument):
    NAME = "Minitaur"
    DEVICE_NAME = "minitaur editor(x64)"
    PRESET_EXTENSION = ".syx"
    TRACK_COLOR = ColorEnum.MINITAUR
    CAN_BE_SHOWN = True
    EXTERNAL_INSTRUMENT_DEVICE = DeviceEnum.EXTERNAL_AUDIO_EFFECT
    AUDIO_INPUT_ROUTING_CHANNEL = InputRoutingChannelEnum.POST_FX
    PRESETS_PATH = "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"
    PROGRAM_CHANGE_OFFSET = 1
    HAS_TOTAL_RECALL = False

    def validate_configuration(self):  # type: () -> bool
        external_synth_track = cast(ExternalSynthTrack, self.track.abstract_track)
        return external_synth_track.midi_track.get_device_from_enum(DeviceEnum.USAMO) is not None

    def show_hide(self):
        # type: () -> Sequence
        """ Only one vst instance of minitaur active: the last one """
        minitaur_tracks = [abt for abt in self.song.abstract_tracks if isinstance(abt.instrument, InstrumentMinitaur)]
        if self.track.abstract_track != minitaur_tracks[-1]:
            return minitaur_tracks[-1].instrument.show_hide()
        else:
            if not len(self.song.armed_tracks):
                return super(InstrumentMinitaur, self).show_hide()

            armed_track = self.song.armed_tracks[0]
            if isinstance(armed_track.instrument,
                          InstrumentMinitaur) and armed_track != self.track.abstract_track and self.track.abstract_track == self.song.current_track:
                self.system.show_hide_plugins()
                return armed_track.select()
            else:
                return super(InstrumentMinitaur, self).show_hide()
