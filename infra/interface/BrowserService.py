from functools import partial

import Live

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceLoadedEvent import DeviceLoadedEvent
from protocol0.domain.lom.instrument.preset.SampleSelectedEvent import SampleSelectedEvent
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.interface.BrowserLoaderService import BrowserLoaderService
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
        browser_name = device_enum.browser_name
        if browser_name.endswith(".adv") or browser_name.endswith(".adg"):
            load_func = partial(self._browser_loader_service.load_from_user_library, browser_name)
        else:
            load_func = partial(self._browser_loader_service.load_device, browser_name)

        seq.add(load_func)
        seq.wait(20)
        seq.add(ApplicationViewFacade.focus_detail)
        seq.add(partial(DomainEventBus.emit, DeviceLoadedEvent(device_enum)))
        return seq.done()

    def load_sample(self, name):
        # type: (str) -> Sequence
        self._browser_loader_service.load_sample(name)
        seq = Sequence()
        seq.wait(10)
        return seq.done()

    def load_from_user_library(self, name):
        # type: (str) -> Sequence
        self._browser_loader_service.load_from_user_library(name)
        seq = Sequence()
        seq.wait(20)
        return seq.done()

    def load_drum_pad_sample(self, name):
        # type: (str) -> Sequence
        ApplicationViewFacade.toggle_browse()
        self._browser_loader_service.load_sample(name)
        seq = Sequence()
        # seq.wait(2)
        seq.add(ApplicationViewFacade.toggle_browse)
        return seq.done()

    def _on_sample_selected_event(self, event):
        # type: (SampleSelectedEvent) -> None
        item = self._browser_loader_service.get_sample(sample_name=event.sample_name)

        if item is not None and item.is_loadable:
            # noinspection PyArgumentList
            self._browser.load_item(item)  # or _browser.preview_item

