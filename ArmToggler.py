from _Framework.ButtonElement import ButtonElement
from _Framework.ControlSurfaceComponent import ControlSurfaceComponent
from _Framework.SubjectSlot import subject_slot

class ArmToggler(ControlSurfaceComponent):

    def __init__(self, *a, **k):
        super(ArmToggler, self).__init__(*a, **k)
        self.last_gq_value = 4
        self._button = None # type: ButtonElements

    def disconnect(self):
        super(ArmToggler, self).disconnect()
        self._button = None

    def set_toggle_button(self, button):
        # type: (ButtonElement) -> None
        self._button = button
        self._on_toggle_button_value.subject = button

    @subject_slot('value')
    def _on_toggle_button_value(self, value):
        if value:
            current = self.song().clip_trigger_quantization
            if current == 0:
                self.song().clip_trigger_quantization = self.last_gq_value
            else:
                self.last_gq_value = current
                self.song().clip_trigger_quantization = 0
