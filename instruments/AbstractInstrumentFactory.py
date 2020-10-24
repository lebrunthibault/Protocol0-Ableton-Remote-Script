from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument
from ClyphX_Pro.clyphx_pro.user_actions.instruments.InstrumentMinitaur import InstrumentMinitaur
from ClyphX_Pro.clyphx_pro.user_actions.instruments.InstrumentNull import InstrumentNull
from ClyphX_Pro.clyphx_pro.user_actions.instruments.InstrumentProphet import InstrumentProphet


class AbstractInstrumentFactory:
    @staticmethod
    def create_from_simple_track(simple_track):
        # type: (SimpleTrack) -> AbstractInstrument
        if simple_track.g_track:
            if simple_track.g_track.is_prophet_group_track:
                return InstrumentProphet()
            elif simple_track.g_track.is_minitaur_group_track:
                return InstrumentMinitaur()
            else:
                return InstrumentNull()


