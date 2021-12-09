from typing import Optional, Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.sequence.Sequence import Sequence


# noinspection PyArgumentList
class NavigationManager(AbstractControlSurfaceComponent):
    """ NavAndViewActions provides navigation and view-related methods. """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(NavigationManager, self).__init__(*a, **k)
        self._app_view = self.application.view

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

    def show_device_view(self):
        # type: () -> None
        """ Shows track view. """
        self._app_view.show_view('Detail')
        self._app_view.show_view('Detail/DeviceChain')

    def show_session(self):
        # type: () -> None
        self._app_view.show_view('Session')

    def show_arrangement(self):
        # type: () -> None
        self._app_view.show_view('Arranger')

    def focus_detail(self):
        # type: () -> None
        """ Moves the focus to the detail view. """
        self._focus_view("Detail")

    def focus_main(self):
        # type: () -> None
        """ Moves the focus to the main focus. """
        self._app_view.focus_view('')

    def _focus_view(self, view):
        # type: (str) -> None
        """ Moves the focus to the given view, showing it first if needed. """
        if not self._app_view.is_view_visible(view):
            self._app_view.show_view(view)
        self._app_view.focus_view(view)
