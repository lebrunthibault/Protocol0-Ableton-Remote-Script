from typing import List

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.controls.MultiEncoder import MultiEncoder


class AbstractActionManager(AbstractControlSurfaceComponent):
    """
        An action manager represents a group of 16 encoder available on the ec4
        It responds on a midi channel to cc messages
        has_shift controls the shift functionality
        See MultiEncoder to configure an encoder
    """
    def __init__(self, channel, has_shift=False, record_actions_as_global=False, *a, **k):
        # type: (int) -> None
        super(AbstractActionManager, self).__init__(*a, **k)
        self.channel = channel
        self.encoders = []  # type: List[MultiEncoder]
        self._current_action = None  # type: callable
        # allows recording actions at the top script level allowing last action re execution in very specific cases
        self.record_actions_as_global = record_actions_as_global

        # shift encoder
        if has_shift:
            self.add_encoder(identifier=1,
                             on_press=lambda: setattr(MultiEncoder, "SHIFT_PRESSED", True),
                             on_release=lambda: setattr(MultiEncoder, "SHIFT_PRESSED", False))

    def add_encoder(self, *a, **k):
        # type: () -> MultiEncoder
        encoder = MultiEncoder(action_manager=self, channel=self.channel, *a, **k)
        self.encoders.append(encoder)
        return encoder

    @property
    def current_action(self):
        return self._current_action
    
    @current_action.setter
    def current_action(self, current_action):
        self._current_action = current_action
        if self.record_actions_as_global:
            self.parent.current_action = current_action
