from functools import partial

import Live
from typing import Optional, cast

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceLoadedEvent import DeviceLoadedEvent
from protocol0.domain.lom.instrument.InstrumentDisplayService import InstrumentDisplayService
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.track.simple_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyReturnTrack import SimpleDummyReturnTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class DeviceService(object):
    def __init__(self, device_component, browser_service, instrument_display_service):
        # type: (DeviceComponent, BrowserServiceInterface, InstrumentDisplayService) -> None
        self._browser_service = browser_service
        self._device_component = device_component
        self._instrument_display_service = instrument_display_service
        DomainEventBus.subscribe(DeviceLoadedEvent, self._on_device_loaded_event)

    def load_device(self, device_name):
        # type: (str) -> Sequence
        device_enum = DeviceEnum.from_value(device_name.upper())  # type: DeviceEnum
        track = self._track_to_select(device_enum)

        track.device_insert_mode = Live.Track.DeviceInsertMode.selected_right

        seq = Sequence()
        seq.add(track.select)
        if device_enum == DeviceEnum.REV2_EDITOR and track.instrument:
            seq.add(partial(track.devices.delete, track.instrument.device))

        seq.add(partial(self._browser_service.load_device_from_enum, device_enum))

        if device_enum == DeviceEnum.REV2_EDITOR:
            seq.add(partial(self._instrument_display_service.activate_plugin_window, track))

        return seq.done()

    def select_or_load_device(self, device_name):
        # type: (str) -> Optional[Sequence]
        device_enum = DeviceEnum.from_value(device_name.upper())  # type: DeviceEnum
        track = self._track_to_select(device_enum)

        devices = track.devices.get_from_enum(device_enum)
        if len(devices) == 0 or device_enum == DeviceEnum.REV2_EDITOR:
            return self.load_device(device_name)

        if track.devices.selected in devices and SongFacade.selected_track() != track:
            next_device = track.devices.selected
        else:
            next_device = ValueScroller.scroll_values(devices, track.devices.selected, True)

        self._device_component.select_device(track, next_device)
        return None

    def _track_to_select(self, device_enum):
        # type: (DeviceEnum) -> SimpleTrack
        track = SongFacade.selected_track()

        # only case when we want to select the midi track of an ext track
        if isinstance(track, SimpleMidiExtTrack) and device_enum == DeviceEnum.REV2_EDITOR:
            return track

        # we always want the group track except if it's the dummy track
        elif isinstance(track, (SimpleMidiExtTrack, SimpleAudioExtTrack, SimpleDummyReturnTrack)):
            return cast(SimpleTrack, track.group_track)

        return track  # type: ignore[unreachable]

    def _on_device_loaded_event(self, event):
        # type: (DeviceLoadedEvent) -> None
        """Select the default parameter if it exists"""
        device = SongFacade.selected_track().devices.selected
        if event.device_enum.default_parameter:
            parameter = device.get_parameter_by_name(event.device_enum.default_parameter)
            self._device_component.selected_parameter = parameter

    def scroll_selected_parameter(self, go_next):
        # type: (bool) -> None
        param = SongFacade.selected_parameter()
        if param is None:
            raise Protocol0Warning("There is no selected parameter")

        param.scroll(go_next)
