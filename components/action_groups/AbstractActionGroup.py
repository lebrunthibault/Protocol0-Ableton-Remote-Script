from typing import List, Optional, Any, Callable

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.interface.EncoderAction import EncoderAction
from protocol0.interface.MultiEncoder import MultiEncoder


class AbstractActionGroup(AbstractControlSurfaceComponent):
    """
    An action group represents a group of 16 encoder available on my faderfox ec4
    It responds on a midi channel to cc messages
    See MultiEncoder to configure an encoder
    """

    def __init__(self, channel, *a, **k):
        # type: (int, Any, Any) -> None
        assert 1 <= channel <= 16
        super(AbstractActionGroup, self).__init__(*a, **k)
        self.channel = channel - 1  # as to match to ec4 channels going from 1 to 16
        self.multi_encoders = []  # type: List[MultiEncoder]

    def _add_multi_encoder(self, multi_encoder):
        # type: (MultiEncoder) -> MultiEncoder
        assert (
                len([encoder for encoder in self.multi_encoders if encoder.identifier == multi_encoder.identifier]) == 0
        ), ("duplicate multi encoder with id %s" % multi_encoder.identifier)
        self.multi_encoders.append(multi_encoder)
        return multi_encoder

    def add_encoder(self, identifier, name, filter_active_tracks=False, on_press=None, on_long_press=None,
                    on_scroll=None):
        # type: (int, str, bool, Optional[Callable], Optional[Callable], Optional[Callable]) -> MultiEncoder
        encoder = MultiEncoder(group=self, identifier=identifier, name=name, filter_active_tracks=filter_active_tracks)
        for action in EncoderAction.make_actions(name=name, on_press=on_press, on_long_press=on_long_press, on_scroll=on_scroll):
            encoder.add_action(action)
        return self._add_multi_encoder(encoder)
