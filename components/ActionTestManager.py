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
        self.parent.log_debug(self.song.selected_track.available_input_routing_types[-1])
        self.parent.log_debug(self.song.selected_track.available_input_routing_types[-1].display_name)
        self.parent.log_debug(self.song.selected_track.available_input_routing_types[-1].attached_object)
        # self.song.selected_track._track.input_routing_type = None  # No input
        # self.song.selected_track._track.input_routing_type = self.song.selected_track.available_input_routing_types[-1]  # No input
        # self.parent.log_debug(self.song.selected_track._track.current_input_routing) # No input
        self.song.selected_track._track.current_input_routing = "No Input"  # No input
        # self.parent.log_debug(self.song.selected_track._current_input_routing)
        # self.song.selected_track._input_routing_type = self.song.selected_track.available_input_routing_types[-1]  # No input
