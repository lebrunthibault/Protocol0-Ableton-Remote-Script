from typing import TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument
from ClyphX_Pro.clyphx_pro.user_actions.instruments.InstrumentMinitaur import InstrumentMinitaur
from ClyphX_Pro.clyphx_pro.user_actions.instruments.InstrumentNull import InstrumentNull
from ClyphX_Pro.clyphx_pro.user_actions.instruments.InstrumentProphet import InstrumentProphet
from ClyphX_Pro.clyphx_pro.user_actions.instruments.InstrumentSimpler import InstrumentSimpler
from ClyphX_Pro.clyphx_pro.user_actions.utils.log import log_ableton

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack

class AbstractInstrumentFactory:
    @staticmethod
    def create_from_simple_track(simple_track):
        # type: ("SimpleTrack") -> AbstractInstrument
        if simple_track.g_track:
            if simple_track.g_track.is_prophet_group_track:
                return InstrumentProphet(simple_track)
            elif simple_track.g_track.is_minitaur_group_track:
                log_ableton("instantiate instrumentminitaur ")
                return InstrumentMinitaur(simple_track)
            else:
                return InstrumentNull(simple_track)

        if simple_track.is_simpler:
            return InstrumentSimpler(simple_track)

        return InstrumentNull(simple_track)


