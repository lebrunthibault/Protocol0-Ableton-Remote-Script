from typing import Optional, Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.sequence.Sequence import Sequence


class NavigationManager(AbstractControlSurfaceComponent):
    """ NavAndViewActions provides navigation and view-related methods. """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(NavigationManager, self).__init__(*a, **k)
        self._app_view = self.application().view

    @property
    def is_session_visible(self):
        # type: () -> bool
        return self._app_view.is_view_visible('Session')

    @property
    def is_arrangement_visible(self):
        # type: () -> bool
        return not self.is_session_visible

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
        # type: () -> Optional[Sequence]
        self.system.show_device_view()
        seq = Sequence()
        seq.add(wait=2)  # apparently live interface refresh is not instant
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
