from functools import partial

import Live
from typing import Optional, cast

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceLoadedEvent import DeviceLoadedEvent
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.simple_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.SimpleDummyReturnTrack import SimpleDummyReturnTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class DeviceService(object):
    def __init__(
        self, track_crud_component, device_component, browser_service
    ):
        # type: (TrackCrudComponent, DeviceComponent, BrowserServiceInterface) -> None
        self._track_crud_component = track_crud_component
        self._device_component = device_component
        self._browser_service = browser_service
        DomainEventBus.subscribe(DeviceLoadedEvent, self._on_device_loaded_event)

    def load_device(self, enum_name):
        # type: (str) -> Sequence
        device_enum = DeviceEnum[enum_name]
        track = self._track_to_select(device_enum)

        track.device_insert_mode = Live.Track.DeviceInsertMode.selected_right

        seq = Sequence()
        seq.add(track.select)
        if device_enum.is_instrument:
            seq.add(self._track_crud_component.create_midi_track)
            seq.add(lambda: setattr(SongFacade.selected_track(), "name", device_enum.value))

        seq.add(partial(self._browser_service.load_device_from_enum, device_enum))

        return seq.done()

    def select_or_load_device(self, enum_name):
        # type: (str) -> Optional[Sequence]
        device_enum = DeviceEnum[enum_name]
        from protocol0.shared.logging.Logger import Logger
        Logger.dev(enum_name)
        Logger.dev(device_enum)
        track = self._track_to_select(device_enum)

        devices = track.devices.get_from_enum(device_enum)
        if len(devices) == 0 or device_enum.is_instrument:
            return self.load_device(enum_name)

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

        return track

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

        # saturator make up gain
        if param.name == DeviceParameterEnum.SATURATOR_DRIVE.parameter_name:
            device = find_if(
                lambda d: param in d.parameters,
                SongFacade.selected_track().devices.get_from_enum(DeviceEnum.SATURATOR),
            )
            saturator_output = device.get_parameter_by_name(
                DeviceParameterEnum.SATURATOR_OUTPUT
            )

            saturator_output.value = -param.value
