from _Framework.ButtonElement import ButtonElement

from ableton.v2.control_surface.control import ButtonControl
from pushbase.transport_component import TransportComponent


class P0TransportComponent(TransportComponent):
    stop_button = ButtonControl()

    @stop_button.released
    def _on_stop_button_released(self, _):
        # type: (ButtonElement) -> None
        self.song.is_playing = False
        # adding this
        self.song.stop_all_clips()
