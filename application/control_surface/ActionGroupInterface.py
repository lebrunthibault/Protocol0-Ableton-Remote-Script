from typing import List, Optional, Callable

from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.control_surface.EncoderAction import EncoderAction
from protocol0.application.control_surface.MultiEncoder import MultiEncoder
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class ActionGroupInterface(object):
    """
    An action group represents a group of 16 encoder available on my control_surface ec4
    It responds on a midi channel to cc messages
    See MultiEncoder to configure an encoder
    """

    CHANNEL = None  # type: Optional[int]

    def __init__(self, container, component_guard):
        # type: (ContainerInterface, Callable) -> None
        super(ActionGroupInterface, self).__init__()
        self._container = container
        self._component_guard = component_guard
        self._multi_encoders = []  # type: List[MultiEncoder]

        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: self._disconnect())

    def _add_multi_encoder(self, multi_encoder):
        # type: (MultiEncoder) -> MultiEncoder
        assert (
            len(
                [
                    encoder
                    for encoder in self._multi_encoders
                    if encoder.identifier == multi_encoder.identifier
                ]
            )
            == 0
        ), "duplicate multi encoder with id %s" % multi_encoder.identifier
        self._multi_encoders.append(multi_encoder)
        return multi_encoder

    def add_encoder(
        self,
        identifier,
        name,
        filter_active_tracks=False,
        on_press=None,
        on_long_press=None,
        on_scroll=None,
    ):
        # type: (int, str, bool, Optional[Callable], Optional[Callable], Optional[Callable]) -> MultiEncoder
        assert self.CHANNEL, "channel not configured for %s" % self
        encoder = MultiEncoder(
            channel=self.CHANNEL - 1,
            identifier=identifier,
            name=name,
            filter_active_tracks=filter_active_tracks,
            component_guard=self._component_guard,
        )
        for action in EncoderAction.make_actions(
            name=name, on_press=on_press, on_long_press=on_long_press, on_scroll=on_scroll
        ):
            encoder.add_action(action)
        return self._add_multi_encoder(encoder)

    def configure(self):
        # type: () -> None
        raise NotImplementedError

    def _disconnect(self):
        # type: () -> None
        for encoder in self._multi_encoders:
            encoder.disconnect()
