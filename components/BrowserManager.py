from functools import partial

from ClyphX_Pro.clyphx_pro.actions.BrowserActions import BrowserActions
from typing import Callable, Optional, Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.errors.Protocol0Error import Protocol0Error
from protocol0.lom.device.Device import Device
from protocol0.lom.device.DeviceType import DeviceType
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.utils import find_if


class BrowserManager(BrowserActions, AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        self._browser = self.application().browser
        self._audio_effect_rack_cache = {}
        super(BrowserManager, self).__init__(*a, **k)

    def load_any_device(self, device_type, device_name):
        # type: (DeviceType, str) -> Sequence
        seq = Sequence()
        if str(device_type) == DeviceType.RACK_DEVICE:
            load_func = partial(self._load_rack_device, device_name)  # type: Callable[[str], Optional[Sequence]]
        elif str(device_type) == DeviceType.PLUGIN_DEVICE:
            load_func = partial(self._load_plugin, device_name)
        elif str(device_type) == DeviceType.ABLETON_DEVICE:
            load_func = partial(self._load_device, device_name)
        else:
            raise Protocol0Error("DeviceType not handled : %s" % device_type)

        seq.add(load_func, check_timeout=15, name="loading device %s" % device_name)

        return seq.done()

    def _load_rack_device(self, rack_name):
        # type: (str) -> Sequence
        seq = Sequence()
        seq.add(
            partial(self.load_from_user_library, None, "'%s.adg'" % rack_name),
            complete_on=lambda: find_if(lambda d: d.name == rack_name, self.song.selected_track.devices),
            check_timeout=10,
            silent=True,
        )
        return seq.done()

    def load_sample(self, sample_name, **k):
        # type: (str) -> None
        self._cache_category("samples")
        item = self._cached_browser_items["samples"].get(sample_name.decode("utf-8"), None)
        if item and item.is_loadable:
            self.song.selected_track.device_insert_mode = self._insert_mode
            self.parent.defer(partial(self._browser.load_item, item))

    def _load_device(self, device_name):
        # type: (str) -> None
        super(BrowserManager, self).load_device(None, "'%s'" % device_name)

    def _load_plugin(self, plugin_name):
        # type: (str) -> None
        super(BrowserManager, self).load_plugin(None, "'%s'" % plugin_name)

    def swap(self, value, **k):
        # type: (str) -> None
        if value == ">" or value == "<":
            super(BrowserManager, self).swap(None, value)
        else:
            super(BrowserManager, self).swap(None, '"%s.adg"' % value)

    def update_audio_effect_preset(self, device):
        # type: (Device) -> Optional[Sequence]
        seq = Sequence()
        device_name = device.name
        device.track.delete_device(device=device)
        preset_item = self._get_audio_effect_preset_item(device_name)
        if not preset_item:
            self.parent.log_warning("Couldn't find preset item")
            return None
        seq.add(partial(self._browser.load_item, preset_item), wait=3)
        return seq.done()

    def _get_audio_effect_preset_item(self, preset_name):
        # type: (str) -> Optional[Live.Browser.BrowserItem]
        if preset_name in self._audio_effect_rack_cache:
            return self._audio_effect_rack_cache[preset_name]
        else:
            audio_effect_rack_item = find_if(lambda i: i.name == "Audio Effect Rack",
                                             self._browser.audio_effects.iter_children)
            if not audio_effect_rack_item:
                self.parent.log_info("Couldn't access preset items for Audio Effect Rack")
                return None
            else:
                preset = find_if(lambda i: i.name == "%s.adg" % preset_name, audio_effect_rack_item.iter_children)
                self._audio_effect_rack_cache[preset_name] = preset
                return preset
