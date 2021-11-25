from protocol0.devices.AbstractExternalSynthTrackInstrument import AbstractExternalSynthTrackInstrument
from protocol0.enums.ColorEnum import ColorEnum


class InstrumentMinitaur(AbstractExternalSynthTrackInstrument):
    NAME = "Minitaur"
    DEVICE_NAME = "minitaur editor(x64)"
    PRESET_EXTENSION = ".syx"
    TRACK_COLOR = ColorEnum.MINITAUR
    CAN_BE_SHOWN = False
    PRESETS_PATH = "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"
    PROGRAM_CHANGE_OFFSET = 1

    EXTERNAL_INSTRUMENT_DEVICE_HARDWARE_LATENCY = 18

# def show_hide(self):
#     # type: () -> Sequence
#     """ Only one vst instance of minitaur active: the last one """
#     minitaur_tracks = [abt for abt in self.song.abstract_tracks if isinstance(abt.instrument, InstrumentMinitaur)]
#     if self.track.abstract_track != minitaur_tracks[-1]:
#         return minitaur_tracks[-1].instrument.show_hide()
#     else:
#         if not len(self.song.armed_tracks):
#             return super(InstrumentMinitaur, self).show_hide()
#
#         armed_track = self.song.armed_tracks[0]
#         if isinstance(armed_track.instrument,
#                       InstrumentMinitaur) and armed_track != self.track.abstract_track and self.track.abstract_track == self.song.current_track:
#             self.system.show_hide_plugins()
#             return armed_track.select()
#         else:
#             return super(InstrumentMinitaur, self).show_hide()
