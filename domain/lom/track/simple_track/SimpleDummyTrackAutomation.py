from functools import partial

import Live
from typing import Optional, cast

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.domain.lom.clip.DummyClip import DummyClip
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.track.simple_track.SimpleDummyTrackAddedEvent import \
    SimpleDummyTrackAddedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackClipSlots import SimpleTrackClipSlots
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class SimpleDummyTrackAutomation(object):
    def __init__(self, live_track, clip_slots, devices):
        # type: (Live.Track.Track, SimpleTrackClipSlots, SimpleTrackDevices) -> None
        self._live_track = live_track
        self._clip_slots = clip_slots
        self._devices = devices
        self._current_parameter_type = None  # type: Optional[str]
        DomainEventBus.subscribe(SimpleDummyTrackAddedEvent,
                                 self._on_simply_dummy_track_added_event)

    def _on_simply_dummy_track_added_event(self, event):
        # type: (SimpleDummyTrackAddedEvent) -> Optional[Sequence]
        # creating automation
        if event.track != self._live_track:
            return None

        seq = Sequence()
        seq.add(self._select_parameters)
        seq.add(self._insert_device)
        seq.wait(5)
        seq.add(self.insert_dummy_clip)
        seq.add(self._create_dummy_automation)
        return seq.done()

    def _select_parameters(self):
        # type: () -> Sequence
        parameters = [enum.name for enum in DeviceParameterEnum.automatable_parameters()]
        parameters.insert(0, "Empty")
        seq = Sequence()
        seq.select(question="Automated parameter", options=parameters)
        seq.add(lambda: setattr(self, "_current_parameter_type", seq.res))
        return seq.done()

    def _insert_device(self):
        # type: () -> Optional[Sequence]
        if self._current_parameter_type == "Empty":
            return None

        parameter_enum = cast(DeviceParameterEnum,
                              DeviceParameterEnum.from_value(self._current_parameter_type))
        return CommandBus.dispatch(
            LoadDeviceCommand(DeviceEnum.from_device_parameter(parameter_enum).name))

    def insert_dummy_clip(self):
        # type: () -> Optional[Sequence]
        if SongFacade.template_dummy_clip_slot() is None:
            raise Protocol0Error("Template dummy clip does not exists")

        seq = Sequence()
        seq.add(partial(SongFacade.template_dummy_clip_slot().duplicate_clip_to,
                        self._clip_slots.selected))
        seq.add(self._configure_dummy_clip)
        seq.wait(2)
        return seq.done()

    def _configure_dummy_clip(self):
        # type: () -> None
        clip = cast(DummyClip, self._clip_slots.clips[0])
        clip.muted = False
        # to have to slack for ending envelopes with create one more bar which is not in the loop
        clip.loop.bar_length = SongFacade.selected_scene().bar_length + 1
        clip.show_loop()
        clip.loop.looping = False
        ApplicationViewFacade.show_clip()

    def _create_dummy_automation(self):
        # type: () -> None
        clip = self._clip_slots.selected.clip
        assert clip, "Cannot find clip"
        clip.clip_name.update("")

        if self._current_parameter_type == "Empty":
            return None

        parameter_enum = cast(DeviceParameterEnum,
                              DeviceParameterEnum.from_value(self._current_parameter_type))

        automated_device = self._devices.get_one_from_enum(
            DeviceEnum.from_device_parameter(parameter_enum))
        if automated_device is None:
            raise Protocol0Warning("The automated device was not inserted")

        automated_parameter = automated_device.get_parameter_by_name(parameter_enum)

        if automated_parameter is None:
            raise Protocol0Warning("The automated device has not matching parameter : %s" %
                                   parameter_enum.name)

        clip.automation.select_or_create_envelope(automated_parameter)
        if SongFacade.is_playing():
            clip.fire()
