from typing import Optional, Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.enums.ColorEnum import InterfaceColorEnum
from a_protocol_0.enums.PixelEnum import PixelEnum
from a_protocol_0.sequence.Sequence import Sequence


class NavigationManager(AbstractControlSurfaceComponent):
    """ NavAndViewActions provides navigation and view-related methods. """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(NavigationManager, self).__init__(*a, **k)
        self._app_view = self.application().view

    def show_clip_view(self):
        # type: () -> Optional[Sequence]
        if self._app_view.is_view_visible("Detail/Clip"):
            return None
        else:
            self._app_view.show_view("Detail")
            self._app_view.show_view("Detail/Clip")
            seq = Sequence()
            seq.add(wait=10)
            return seq.done()

    @property
    def is_device_view_visible(self):
        # type: () -> bool
        return self._app_view.is_view_visible(
            "Detail/DeviceChain"
        ) and self.parent.keyboardShortcutManager.pixel_has_color(PixelEnum.SEPARATOR, InterfaceColorEnum.SEPARATOR)

    def show_device_view(self):
        # type: () -> Optional[Sequence]
        self.parent.log_dev(self.is_device_view_visible)
        if self.is_device_view_visible:
            return None
        else:
            self._app_view.show_view("Detail")
            self._app_view.show_view("Detail/DeviceChain")
            self.parent.log_dev(self.is_device_view_visible)
            seq = Sequence()
            seq.add(complete_on=lambda: self.is_device_view_visible)
            seq.add(wait=1)  # apparently live interface refresh is not instant
            return seq.done()

    def focus_main(self):
        # type: () -> None
        """ Moves the focus to the main focus. """
        self._app_view.focus_view("")

    def focus_detail(self):
        # type: () -> None
        """ Moves the focus to the detail view. """
        self._focus_view("Detail")

    def _focus_view(self, view):
        # type: (str) -> None
        """ Moves the focus to the given view, showing it first if needed. """
        if not self._app_view.is_view_visible(view):
            self._app_view.show_view(view)
        self._app_view.focus_view(view)
