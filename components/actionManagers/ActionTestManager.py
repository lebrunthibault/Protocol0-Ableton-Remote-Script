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
        self.previous_instrument = None
        self.previous_live_id = None

    @button_action()
    def action_test(self):
        self.parent.show_message("hello")

    @button_action()
    def action_test_state(self):
        self.parent.log_info(self.previous_instrument)
        self.parent.log_info(self.song.selected_track.instrument.device._device)
        self.parent.log_info(self.song.selected_track.instrument.device._device._live_ptr)
        self.parent.log_info(self.previous_instrument == self.song.selected_track.instrument.device._device)
        self.parent.log_info(self.previous_live_id == self.song.selected_track.instrument.device._device._live_ptr)
        self.previous_instrument = self.song.selected_track.instrument.device._device
        self.previous_live_id = self.song.selected_track.instrument.device._device._live_ptr
