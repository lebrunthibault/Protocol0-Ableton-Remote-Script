from functools import partial

from ClyphX_Pro.clyphx_pro.actions.BrowserActions import BrowserActions
from typing import Optional, Any

import Live
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils import find_if
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class BrowserService(BrowserActions, BrowserServiceInterface):
    def __init__(self):
        # type: () -> None
        super(BrowserService, self).__init__()
        self._audio_effect_rack_cache = {}

    def load_device_from_enum(self, device_enum):
        # type: (DeviceEnum) -> Sequence
        seq = Sequence()
        browser_name = "'%s'" % device_enum.browser_name
        if device_enum.is_device:
            load_func = partial(self.load_device, None, browser_name)
        elif device_enum.is_user:
            load_func = partial(self.load_from_user_library, None, browser_name)
        else:
            raise Protocol0Error("Couldn't load device %s, configure is_device or is_rack" % device_enum)

        seq.add(load_func, complete_on=SongFacade.selected_track()._devices_listener)
        return seq.done()

    def load_sample(self, sample_name, **k):
        # type: (str, Any) -> None
        item = self._get_sample(sample_name=sample_name)
        if item and item.is_loadable:
            SongFacade.selected_track().device_insert_mode = self._insert_mode
            # noinspection PyArgumentList
            self._browser.load_item(item)  # or _browser.preview_item

    def _get_sample(self, sample_name):
        # type: (str) -> Live.Browser.BrowserItem
        self._cache_category("samples")
        return self._cached_browser_items["samples"].get(sample_name.decode("utf-8"), None)

    def update_audio_effect_preset(self, device):
        # type: (Device) -> Optional[Sequence]
        seq = Sequence()
        device_name = device.name
        device.delete()
        preset_item = self._get_audio_effect_preset_item(device_name)
        if not preset_item:
            Logger.log_warning("Couldn't find preset item")
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
                Logger.log_info("Couldn't access preset items for Audio Effect Rack")
                return None
            else:
                preset = find_if(lambda i: i.name == "%s.adg" % preset_name, audio_effect_rack_item.iter_children)
                self._audio_effect_rack_cache[preset_name] = preset
                return preset
