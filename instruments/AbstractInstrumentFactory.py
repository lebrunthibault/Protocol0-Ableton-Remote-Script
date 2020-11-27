from typing import TYPE_CHECKING

from a_protocol_0.instruments.AbstractInstrument import AbstractInstrument
from a_protocol_0.instruments.InstrumentMinitaur import InstrumentMinitaur
from a_protocol_0.instruments.InstrumentNull import InstrumentNull
from a_protocol_0.instruments.InstrumentProphet import InstrumentProphet
from a_protocol_0.instruments.InstrumentSimpler import InstrumentSimpler
from a_protocol_0.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.AbstractTrack import AbstractTrack


class AbstractInstrumentFactory(object):
    @staticmethod
    def create_from_abstract_track(track):
        # type: ("AbstractTrack") -> AbstractInstrument
        from a_protocol_0.lom.track.SimpleTrack import SimpleTrack
        if isinstance(track, SimpleTrack):
            if track.is_simpler:
                return InstrumentSimpler(track)
            else:
                return InstrumentNull(track)

        from a_protocol_0.lom.track.GroupTrack import GroupTrack
        if isinstance(track, GroupTrack):
            if track.name == TrackName.GROUP_PROPHET_NAME:
                return InstrumentProphet(track.midi)
            if track.name == TrackName.GROUP_MINITAUR_NAME:
                return InstrumentMinitaur(track.midi)
            else:
                raise Exception("Invalid GroupTrack name")
