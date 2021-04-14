from typing import List

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.controls.EncoderAction import EncoderAction
from a_protocol_0.controls.EncoderModifier import EncoderModifierEnum, EncoderModifier
from a_protocol_0.controls.MultiEncoder import MultiEncoder
from a_protocol_0.controls.MultiEncoderModifier import MultiEncoderModifier


class AbstractActionGroup(AbstractControlSurfaceComponent):
    """
        An action group represents a group of 16 encoder available on my faderfox ec4
        It responds on a midi channel to cc messages
        See MultiEncoder to configure an encoder
    """
    def __init__(self, channel, record_actions_as_global=False, *a, **k):
        # type: (int) -> None
        super(AbstractActionGroup, self).__init__(*a, **k)
        self.available_modifiers = [EncoderModifier(type) for type in EncoderModifierEnum]  # type: List[EncoderModifier]
        self.channel = channel
        self.multi_encoders = []  # type: List[MultiEncoder]
        self._current_action = None  # type: callable
        # allows recording actions at the top script level allowing last action re execution in very specific cases
        self.record_actions_as_global = record_actions_as_global

    def _add_multi_encoder(self, multi_encoder):
        # type: (MultiEncoder) -> MultiEncoder
        assert len([encoder for encoder in
                    self.multi_encoders if encoder.identifier == multi_encoder.identifier]) == 0, "duplicate multi encoder"
        self.multi_encoders.append(multi_encoder)
        return multi_encoder

    def add_encoder(self, id, on_press=None, on_long_press=None, on_shift_press=None,
                    on_shift_long_press=None, on_scroll=None, on_shift_scroll=None):
        # type: (int) -> MultiEncoder
        k = locals()
        del k["self"]
        del k["id"]
        encoder = MultiEncoder(action_group=self, channel=self.channel, identifier=id)
        [encoder.add_action(action) for action in EncoderAction.make_actions(**k)]
        return self._add_multi_encoder(encoder)

    def add_modifier(self, id, modifier_type, *a, **k):
        # type: (int, EncoderModifierEnum) -> MultiEncoder
        encoder = MultiEncoderModifier(action_group=self, channel=self.channel, identifier=id,
                                    modifier_type=modifier_type, *a, **k)
        return self._add_multi_encoder(encoder)

    @property
    def current_action(self):
        return self._current_action

    @current_action.setter
    def current_action(self, current_action):
        self._current_action = current_action
        if self.record_actions_as_global:
            self.parent.current_action = current_action
