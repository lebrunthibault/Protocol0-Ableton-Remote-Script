import inspect
from functools import partial

from typing import Dict, List, Type, Callable

from protocol0.domain.lom.scene.PlayingSceneChangedEvent import PlayingSceneChangedEvent
from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.lom.scene.ScenePositionScrolledEvent import ScenePositionScrolledEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.BarEndingEvent import BarEndingEvent
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.func import is_func_equal, get_callable_repr, \
    get_class_from_func
from protocol0.infra.interface.session.SessionUpdatedEvent import SessionUpdatedEvent
from protocol0.infra.midi.MidiBytesReceivedEvent import MidiBytesReceivedEvent
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.types import T


class DomainEventBus(object):
    _DEBUG = True
    _DEBUGGED_EVENTS = (ScenePositionScrolledEvent,)
    # these periodic events are not logged even in debug mode
    _SILENT_EVENTS = (BarChangedEvent, LastBeatPassedEvent, BarEndingEvent,
                      Last32thPassedEvent, SceneLastBarPassedEvent, PlayingSceneChangedEvent,
                      SongStoppedEvent, SessionUpdatedEvent, MidiBytesReceivedEvent)
    _registry = {}  # type: Dict[Type, List[Callable]]

    @classmethod
    def once(cls, domain_event, subscriber):
        # type: (Type[T], Callable) -> None
        """ helper method for unique reaction """

        def execute(event):
            # type: (T) -> None
            subscriber(event)
            cls.un_subscribe(domain_event, execute)

        cls.subscribe(domain_event, execute)

    @classmethod
    def subscribe(cls, domain_event, subscriber, unique_method=False):
        # type: (Type, Callable, bool) -> None
        if domain_event not in cls._registry:
            cls._registry[domain_event] = []

        for sub in cls._registry[domain_event]:
            if is_func_equal(sub, subscriber, unique_method):
                Backend.client().show_warning("duplicate subscriber : %s for event %s" % (sub,
                                                                                          domain_event))
                if inspect.ismethod(sub):
                    Logger.warning("method class: %s <-> %s" % (get_class_from_func(sub),
                                                                get_class_from_func(
                                                                    subscriber)))
                return

        cls._registry[domain_event].append(subscriber)

    @classmethod
    def un_subscribe(cls, domain_event, subscriber):
        # type: (Type, Callable) -> None
        if domain_event in cls._registry and subscriber in cls._registry[domain_event]:
            cls._registry[domain_event].remove(subscriber)

    @classmethod
    def emit(cls, domain_event):
        # type: (object) -> None
        if cls._DEBUG and type(domain_event) not in cls._SILENT_EVENTS:
            Logger.info("Event emitted: %s" % domain_event.__class__.__name__)

        if type(domain_event) in cls._registry:
            # protect the list from unsubscribe in subscribers
            subscribers = cls._registry[type(domain_event)][:]
            if type(domain_event) in cls._DEBUGGED_EVENTS:
                Logger.info("Found subscribers: %s" % [get_callable_repr(sub) for sub in
                                                       subscribers])
            for subscriber in subscribers:
                subscriber(domain_event)

    @classmethod
    def defer_emit(cls, domain_event):
        # type: (object) -> None
        """ for events notified in listeners we can defer to avoid the changes by notification error"""
        Scheduler.defer(partial(cls.emit, domain_event))
