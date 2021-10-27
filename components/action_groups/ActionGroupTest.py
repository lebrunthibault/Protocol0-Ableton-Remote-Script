from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup


class ActionGroupTest(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupTest, self).__init__(channel=0, *a, **k)
        # 1 encoder
        self.add_encoder(identifier=1, name="test", on_press=self.action_test)

    def action_test(self):
        # type: () -> None
        self.parent.log_dev(self.song.selected_track.input_routing_type)
        self.parent.log_dev(self.song.selected_track.input_routing_type.category)
        self.parent.log_dev(self.song.selected_track.input_routing_type.display_name)
        self.parent.log_dev(self.song.selected_track.input_routing_type.attached_object)
        self.parent.log_dev(self.song.selected_track._track.current_input_sub_routing)
        self.parent.log_dev(self.song.selected_track._track.input_routing_channel)
        self.parent.log_dev(self.song.selected_track._track.input_routing_channel.display_name)
