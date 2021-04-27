import Live
import deprecation
from typing import TYPE_CHECKING, Optional

from a_protocol_0.interface.InterfaceState import InterfaceState
from a_protocol_0.lom.device.DeviceParameter import DeviceParameter
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from a_protocol_0.lom.clip.Clip import Clip


# noinspection PyTypeHints
class ClipActionMixin(object):
    @property
    def is_playing(self):
        # type: (Clip) -> bool
        return self._clip and self._clip.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (Clip, bool) -> None
        if self._clip and is_playing != self.is_playing:
            self._clip.is_playing = is_playing

    def select(self):
        # type: (Clip) -> Sequence
        self.song.highlighted_clip_slot = self.clip_slot
        seq = Sequence(silent=True)
        seq.add(self.parent.clyphxNavigationManager.show_clip_view)
        # seq.add(wait=10)
        return seq.done()

    def play(self):
        # type: (Clip) -> None
        self.is_playing = True

    def play_stop(self):
        # type: (Clip) -> None
        self.is_playing = not self.is_playing

    def delete(self):
        # type: (Clip) -> Optional[Sequence]
        if not self._clip:
            return None
        seq = Sequence()
        seq.add(self.clip_slot.delete_clip, complete_on=self.clip_slot._has_clip_listener)
        return seq.done()

    def automation_envelope(self, parameter):
        # type: (Clip, DeviceParameter) -> Live.Clip.AutomationEnvelope
        return self._clip and self._clip.automation_envelope(parameter._device_parameter)

    def show_envelope_parameter(self, parameter):
        # type: (Clip, DeviceParameter) -> None
        self.parent.clyphxNavigationManager.show_clip_view()
        self.view.show_envelope()
        self.view.select_envelope_parameter(parameter._device_parameter)
        if not InterfaceState.CLIP_ENVELOPE_SHOW_BOX_CLICKED:
            self.parent.keyboardShortcutManager.double_click_envelopes_show_box()
            InterfaceState.CLIP_ENVELOPE_SHOW_BOX_CLICKED = True
        self.displayed_automated_parameter = parameter  # type: Optional[DeviceParameter]

    def create_automation_envelope(self, parameter):
        # type: (Clip, DeviceParameter) -> Live.Clip.AutomationEnvelope
        return self._clip.create_automation_envelope(parameter._device_parameter)

    @deprecation.deprecated()
    def clear_all_envelopes(self):
        # type: (Clip) -> None
        if self._clip:
            return self._clip.clear_all_envelopes()

    def configure_new_clip(self):
        # type: (Clip) -> Optional[Sequence]
        """ extended """
        pass

    def refresh_appearance(self):
        # type: (Clip) -> None
        self.clip_name.update()  # type: ignore
        self.color = self.track.default_color
