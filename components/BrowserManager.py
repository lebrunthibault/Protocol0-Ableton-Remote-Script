from functools import partial

from ClyphX_Pro.clyphx_pro.actions.BrowserActions import BrowserActions
from _Framework.Util import find_if
from a_protocol_0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.device.DeviceType import DeviceType
from a_protocol_0.sequence.Sequence import Sequence


class BrowserManager(BrowserActions, AbstractControlSurfaceComponent):
    def load_any_device(self, device_type, device_name):
        # type: (DeviceType, str) -> None
        seq = Sequence()
        if device_type == DeviceType.RACK_DEVICE:
            load_func = partial(self._load_rack_device, device_name)
        elif device_type == DeviceType.PLUGIN_DEVICE:
            load_func = partial(self._load_plugin, device_name)
        elif device_type == DeviceType.ABLETON_DEVICE:
            load_func = partial(self._load_device, device_name)
        else:
            raise Protocol0Error("DeviceType not handled : %s" % device_type)

        seq.add(load_func, check_timeout=15)

        return seq.done()

    def _load_rack_device(self, rack_name, hide=False):
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

    def _load_device(self, device_name):
        # type: (str) -> None
        super(BrowserManager, self).load_device(None, "'%s'" % device_name)

    def _load_plugin(self, plugin_name):
        # type: (str) -> None
        super(BrowserManager, self).load_plugin(None, "'%s'" % plugin_name)

    def swap(self, value):
        # type: (str) -> None
        if value == ">" or value == "<":
            super(BrowserManager, self).swap(None, value)
        else:
            super(BrowserManager, self).swap(None, '"%s.adg"' % value)
