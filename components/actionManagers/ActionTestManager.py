from a_protocol_0.components.actionManagers.AbstractActionManager import AbstractActionManager
from a_protocol_0.utils.decorators import button_action


class ActionTestManager(AbstractActionManager):
    """
        Just a playground to launch test actions
    """
    def __init__(self, *a, **k):
        super(ActionTestManager, self).__init__(channel=0, *a, **k)
        # 1 encoder
        self.add_encoder(id=1, on_press=self.action_test)

    @button_action()
    def action_test(self):
        self.song.current_track.selected_device._view.is_showing_chain_devices = not self.song.current_track.selected_device._view.is_showing_chain_devices