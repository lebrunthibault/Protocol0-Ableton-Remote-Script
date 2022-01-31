from typing import Any

import Live
from protocol0.domain.lom.AbstractObject import AbstractObject


class Application(AbstractObject):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(Application, self).__init__(*a, **k)
        self._application = self.parent.application()  # type: Live.Application.Application

    @property
    def view(self):
        # type: () -> Live.Application.Application.View
        return self._application.view

    @property
    def browser(self):
        # type: () -> Live.Browser.Browser
        return self._application.browser

    @property
    def session_view_active(self):
        # type: () -> bool
        return self.view.is_view_visible('Session')
