from typing import Optional

from protocol0 import EmptyModule
from protocol0.application.Protocol0 import Protocol0
from protocol0.application.control_surface.ActionGroupFactory import ActionGroupFactory
from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.domain.lom.song.SongInitService import SongInitService
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackInterface import MatchingTrackInterface
from protocol0.domain.lom.track.routing.RoutingTrackDescriptor import RoutingTrackDescriptor
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.func import nop
from protocol0.infra.logging.LoggerService import LoggerService
from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
from protocol0.shared.UndoFacade import UndoFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.tests.domain.fixtures.song import AbletonSong
from protocol0.domain.lom.instrument.InstrumentDisplayService import InstrumentDisplayService
from protocol0.tests.infra.scheduler.TickSchedulerTest import TickSchedulerTest


def make_protocol0():
    # type: () -> Protocol0
    live_song = AbletonSong()
    Protocol0.song = lambda _: live_song
    wait = Scheduler.wait
    Scheduler.wait = classmethod(nop)
    monkey_patch_static()
    p0 = Protocol0(EmptyModule(name="c_instance", is_false=False))
    monkey_patch_p0(live_song)
    Scheduler.wait = wait
    return p0


def monkey_patch_static():
    # hide logs
    Logger(LoggerService())
    Logger.dev = classmethod(nop)
    Logger.info = classmethod(nop)
    Logger.warning = classmethod(nop)

    Backend(nop)
    UndoFacade(nop, nop)
    AbletonSet.notify = nop
    SimpleTrack.click = nop
    # noinspection PyTypeChecker
    Scheduler(TickSchedulerTest(), None)  # ignore beat scheduling in tests

    # remove this until fixtures are thorough
    ActionGroupFactory.create_action_groups = classmethod(nop)

    InstrumentDisplayService._on_simple_track_armed_event = nop

    SongInitService.init_song = nop
    MatchingTrackInterface.disconnect = nop
    RoutingTrackDescriptor.__set__ = nop

    def log(_, message, *__, **___):
        print(message)

    Logger._log = classmethod(log)


def monkey_patch_p0(live_song=None):
    # type: (Optional[Live.Song.Song]) -> None
    Scheduler(TickSchedulerTest(), BeatScheduler(live_song))
