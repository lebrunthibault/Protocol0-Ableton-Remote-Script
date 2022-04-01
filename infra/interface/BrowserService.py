from functools import partial

from typing import Optional

import Live
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.preset.SampleSelectedEvent import SampleSelectedEvent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils import find_if
from protocol0.infra.interface.BrowserLoaderService import BrowserLoaderService
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class BrowserService(BrowserServiceInterface):
    def __init__(self, browser, browser_loader_service):
        # type: (Live.Browser.Browser, BrowserLoaderService) -> None
        super(BrowserService, self).__init__()
        self._browser = browser
        self._browser_loader_service = browser_loader_service
        DomainEventBus.subscribe(SampleSelectedEvent, self._on_sample_selected_event)

    def load_device_from_enum(self, device_enum):
        # type: (DeviceEnum) -> Sequence
        seq = Sequence()
        if device_enum.is_user:
            load_func = partial(self._browser_loader_service.load_from_user_library, device_enum.browser_name)
        else:
            load_func = partial(self._browser_loader_service.load_device, device_enum.browser_name)

        seq.add(load_func)
        seq.wait_for_listener(SongFacade.selected_track()._devices_listener)  # type: ignore[arg-type]
        seq.add(ApplicationView.focus_detail)
        return seq.done()

    def _on_sample_selected_event(self, event):
        # type: (SampleSelectedEvent) -> None
        item = self._get_sample(sample_name=event.sample_name)
        if item and item.is_loadable:
            # noinspection PyArgumentList
            self._browser.load_item(item)  # or _browser.preview_item

    def _get_sample(self, sample_name):
        # type: (str) -> Live.Browser.BrowserItem
        self._browser_loader_service._cache_category("samples")
        return self._browser_loader_service._cached_browser_items["samples"].get(str(sample_name.decode("utf-8")), None)

    def update_audio_effect_preset(self, device):
        # type: (Device) -> Optional[Sequence]
        seq = Sequence()
        device_name = device.name
        device.delete()
        preset_item = self._get_audio_effect_preset_item(device_name)
        if not preset_item:
            Logger.warning("Couldn't find preset item")
            return None
        seq.add(partial(self._browser.load_item, preset_item))
        seq.wait(3)
        return seq.done()

    def _get_audio_effect_preset_item(self, preset_name):
        # type: (str) -> Optional[Live.Browser.BrowserItem]
        audio_effect_rack_item = find_if(lambda i: i.name == "Audio Effect Rack",
                                         self._browser.audio_effects.iter_children)
        if not audio_effect_rack_item:
            Logger.info("Couldn't access preset items for Audio Effect Rack")
            return None
        else:
            preset = find_if(lambda i: i.name == "%s.adg" % preset_name, audio_effect_rack_item.iter_children)
            return preset
