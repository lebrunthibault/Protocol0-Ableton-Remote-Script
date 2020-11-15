from typing import TYPE_CHECKING

from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument
from a_protocol_0.instruments.InstrumentMinitaur import InstrumentMinitaur
from a_protocol_0.instruments.InstrumentNull import InstrumentNull
from a_protocol_0.instruments.InstrumentProphet import InstrumentProphet
from a_protocol_0.instruments.InstrumentSimpler import InstrumentSimpler

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.SimpleTrack import SimpleTrack


class AbstractInstrumentFactory(object):
    @staticmethod
    def create_from_simple_track(simple_track):
        # type: ("SimpleTrack") -> AbstractInstrument
        if simple_track.g_track:
            if simple_track.g_track.is_prophet_group_track:
                return InstrumentProphet(simple_track)
            elif simple_track.g_track.is_minitaur_group_track:
                return InstrumentMinitaur(simple_track)
            else:
                return InstrumentNull(simple_track)

        if simple_track.is_simpler:
            return InstrumentSimpler(simple_track)

        return InstrumentNull(simple_track)
