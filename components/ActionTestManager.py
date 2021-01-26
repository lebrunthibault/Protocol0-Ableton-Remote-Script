from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.controls.MultiEncoder import MultiEncoder
from a_protocol_0.utils.decorators import button_action


class ActionTestManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        super(ActionTestManager, self).__init__(*a, **k)
        # 1 encoder
        MultiEncoder(channel=0, identifier=1,
                     on_press=self.action_test)

    @button_action()
    def action_test(self):
        pass