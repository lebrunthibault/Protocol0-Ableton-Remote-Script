from ClyphX_Pro.clyphx_pro.actions.BrowserActions import BrowserActions
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent


class BrowserManager(BrowserActions, AbstractControlSurfaceComponent):
    def load_rack_device(self, rack_name, hide=False):
        # type: (str) -> None
        self.load_from_user_library(None, "'%s.adg'" % rack_name)
        if hide:
            self.parent.defer(self.parent.keyboardShortcutManager.hide_plugins)

    def load_sample(self, preset_name):
        # type: (str) -> None
        super(BrowserManager, self).load_sample(None, "'%s'" % preset_name)

    def swap(self, value):
        # type: (str) -> None
        if value == ">" or value == "<":
            super(BrowserManager, self).swap(None, value)
        else:
            super(BrowserManager, self).swap(None, '"%s.adg"' % value)

