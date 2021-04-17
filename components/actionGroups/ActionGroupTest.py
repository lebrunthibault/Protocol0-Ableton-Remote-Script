from a_protocol_0.components.actionGroups.AbstractActionGroup import AbstractActionGroup
from a_protocol_0.sequence.Sequence import Sequence


class ActionGroupTest(AbstractActionGroup):
    """
    Just a playground to launch test actions
    """

    def __init__(self, *a, **k):
        super(ActionGroupTest, self).__init__(channel=0, *a, **k)
        # 1 encoder
        self.add_encoder(id=1, name="test", on_press=self.action_test)
        self.previous_instrument = None
        self.previous_live_id = None

    def error(self):
        raise Exception("exception thrown")

    def action_error(self):
        seq = Sequence()
        seq.add(self.error)
        return seq.done()

    def action_test(self):
        self.song.end_undo_step()
        self.song.end_undo_step()
        self.song.end_undo_step()

        # seq = Sequence()
        # seq.add(wait=1)
        # seq.add(self.action_error)
        # return seq.done()

    def action_test_state(self):
        self.error()
        self.parent.log_info(self.previous_instrument)
        self.parent.log_info(self.song.selected_track.instrument.device._device)
        self.parent.log_info(self.song.selected_track.instrument.device._device._live_ptr)
        self.parent.log_info(self.previous_instrument == self.song.selected_track.instrument.device._device)
        self.parent.log_info(self.previous_live_id == self.song.selected_track.instrument.device._device._live_ptr)
        self.previous_instrument = self.song.selected_track.instrument.device._device
        self.previous_live_id = self.song.selected_track.instrument.device._device._live_ptr
