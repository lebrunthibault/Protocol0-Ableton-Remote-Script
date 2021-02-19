from functools import partial

from ClyphX_Pro.clyphx_pro.actions.BrowserActions import BrowserActions
from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.lom.device.AutomationDeviceType import AutomationDeviceType
from a_protocol_0.sequence.Sequence import Sequence


class BrowserManager(BrowserActions, AbstractControlSurfaceComponent):
    def load_any_device(self, device_type, device_name):
        # type: (AutomationDeviceType, str) -> None
        seq = Sequence()
        if device_type == AutomationDeviceType.RACK_DEVICE:
            seq.add(partial(self.load_rack_device, device_name))
        elif device_type == AutomationDeviceType.PLUGIN_DEVICE:
            seq.add(partial(self.load_plugin, device_name))
        elif device_type == AutomationDeviceType.ABLETON_DEVICE:
            seq.add(partial(self.load_device, device_name))
        else:
            raise RuntimeError("DeviceType not handled : %s" % device_type)

        return seq.done()

    def load_rack_device(self, rack_name, hide=False):
        # type: (str, bool) -> None
        seq = Sequence()
        seq.add(partial(self.load_from_user_library, None, "'%s.adg'" % rack_name),
                complete_on=lambda: find_if(lambda d: d.name == rack_name, self.song.selected_track.devices))
        if hide:
            seq.add(self.parent.keyboardShortcutManager.hide_plugins, wait=1)
        return seq.done()

    def load_sample(self, sample_name):
        # type: (str) -> None
        super(BrowserManager, self).load_sample(None, "'%s'" % sample_name)

    def load_device(self, device_name):
        # type: (str) -> None
        super(BrowserManager, self).load_device(None, "'%s'" % device_name)

    def load_plugin(self, plugin_name):
        # type: (str) -> None
        super(BrowserManager, self).load_plugin(None, "'%s'" % plugin_name)

    def swap(self, value):
        # type: (str) -> None
        if value == ">" or value == "<":
            super(BrowserManager, self).swap(None, value)
        else:
            super(BrowserManager, self).swap(None, '"%s.adg"' % value)
