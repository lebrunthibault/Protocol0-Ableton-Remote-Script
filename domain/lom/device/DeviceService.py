from functools import partial

import Live
from typing import Optional, cast

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceLoadedEvent import DeviceLoadedEvent
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.group_track.ext_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.audio.dummy.SimpleDummyReturnTrack import SimpleDummyReturnTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class DeviceService(object):
    def __init__(self, track_crud_component, device_component, browser_service):
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
            seq.add(lambda: setattr(Song.selected_track(), "name", device_enum.value))

        seq.add(partial(self._browser_service.load_device_from_enum, device_enum))

        if (
            device_enum.default_parameter is not None
            and Song.selected_clip(raise_if_none=False) is not None
            and ApplicationViewFacade.is_clip_view_visible()
        ):
            seq.add(partial(self._create_default_automation, Song.selected_clip()))

        return seq.done()

    def select_or_load_device(self, enum_name):
        # type: (str) -> Optional[Sequence]
        device_enum = DeviceEnum[enum_name]
        track = self._track_to_select(device_enum)

        devices = track.devices.get_from_enum(device_enum)
        if len(devices) == 0 or device_enum.is_instrument:
            return self.load_device(enum_name)

        if track.devices.selected in devices and Song.selected_track() != track:
            next_device = track.devices.selected
        else:
            next_device = ValueScroller.scroll_values(devices, track.devices.selected, True)

        self._device_component.select_device(track, next_device)
        return None

    def _track_to_select(self, device_enum):
        # type: (DeviceEnum) -> SimpleTrack
        track = Song.selected_track()

        # only case when we want to select the midi track of an ext track
        if isinstance(track, SimpleMidiExtTrack) and device_enum == DeviceEnum.REV2_EDITOR:
            return track

        # we always want the group track except if it's the dummy track
        elif isinstance(track, (SimpleMidiExtTrack, SimpleAudioExtTrack, SimpleDummyReturnTrack)):
            return cast(SimpleTrack, track.group_track)

        return track

    def _on_device_loaded_event(self, _):
        # type: (DeviceLoadedEvent) -> None
        """Select the default parameter if it exists"""
        device = Song.selected_track().devices.selected
        if device.enum.default_parameter is not None:
            parameter = device.get_parameter_by_name(device.enum.default_parameter)
            self._device_component.selected_parameter = parameter

    def _create_default_automation(self, clip):
        # type: (Clip) -> None
        device = Song.selected_track().devices.selected
        assert device.enum.default_parameter, "Loaded device has no default parameter"
        parameter = device.get_parameter_by_name(device.enum.default_parameter)
        assert parameter is not None, "parameter not found"
        clip.automation.show_parameter_envelope(parameter)

    def scroll_selected_parameter(self, go_next):
        # type: (bool) -> None
        param = Song.selected_parameter()
        if param is None:
            raise Protocol0Warning("There is no selected parameter")

        param.scroll(go_next)

        # saturator make up gain
        if param.name == DeviceParameterEnum.SATURATOR_DRIVE.parameter_name:
            device = find_if(
                lambda d: param in d.parameters,
                Song.selected_track().devices.get_from_enum(DeviceEnum.SATURATOR),
            )
            saturator_output = device.get_parameter_by_name(DeviceParameterEnum.SATURATOR_OUTPUT)

            saturator_output.value = -param.value
