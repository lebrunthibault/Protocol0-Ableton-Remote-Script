from typing import Optional, Any

from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
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
            seq.add(wait=1)
            return seq.done()

    def show_track_view(self):
        # type: () -> Optional[Sequence]
        if self._app_view.is_view_visible("Detail/DeviceChain"):
            return None
        else:
            self._app_view.show_view("Detail")
            self._app_view.show_view("Detail/DeviceChain")
            seq = Sequence()
            seq.add(wait=1)
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
