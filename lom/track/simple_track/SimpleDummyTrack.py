from functools import partial

from typing import Optional, Any

from protocol0.enums.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.enums.DeviceParameterEnum import DeviceParameterEnum
from protocol0.enums.InputRoutingTypeEnum import InputRoutingTypeEnum
from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.sequence.Sequence import Sequence


class SimpleDummyTrack(SimpleAudioTrack):
    KEEP_CLIPS_ON_ADDED = True

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        self.parameter_type = None  # type: Optional[str]
        self.clip_bar_length = 1
        self.parameter_enum = None  # type: Optional[DeviceParameterEnum]
        super(SimpleDummyTrack, self).__init__(*a, **k)

    def _added_track_init(self):
        # type: () -> Sequence
        self.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self.input_routing.type = InputRoutingTypeEnum.NO_INPUT
        seq = Sequence()
        seq.add(super(SimpleDummyTrack, self)._added_track_init)

        # creating automation
        seq = Sequence()
        seq.add(self._select_parameters)
        seq.add(self._insert_device)
        seq.add(wait=5)
        seq.add(self._insert_dummy_clip)
        seq.add(self._create_dummy_automation)
        return seq.done()

    @property
    def computed_base_name(self):
        # type: () -> str
        return "dummy %d" % (self.abstract_group_track.dummy_tracks.index(self) + 1)

    @property
    def computed_color(self):
        # type: () -> int
        return self.group_track.color

    def _select_parameters(self):
        # type: () -> Sequence
        parameters = [enum.name for enum in DeviceParameterEnum.automatable_parameters()]
        seq = Sequence()
        seq.select(question="Automated parameter", options=parameters)
        seq.add(lambda: setattr(self, "parameter_type", seq.res))
        # seq.select(question="Clip bar length",
        #            options=self.parent.utilsManager.get_bar_length_list(bar_length=self.song.selected_scene.bar_length),
        #            vertical=False)
        # seq.add(lambda: setattr(self, "clip_bar_length", seq.response()))
        return seq.done()

    def _insert_device(self):
        # type: () -> Optional[Sequence]
        self.parameter_enum = DeviceParameterEnum.from_value(self.parameter_type)
        return self.parent.browserManager.load_device_from_enum(self.parameter_enum.device_enum)

    def _insert_dummy_clip(self):
        # type: () -> Optional[Sequence]
        if not self.song.template_dummy_clip or len(self.clips):
            return None

        cs = self.clip_slots[self.song.selected_scene.index]
        seq = Sequence()
        seq.add(partial(self.song.template_dummy_clip.clip_slot.duplicate_clip_to, cs))
        seq.add(lambda: setattr(self.clips[0], "muted", False))
        seq.add(wait=2)
        return seq.done()

    def _create_dummy_automation(self):
        # type: () -> None
        clip = self.clip_slots[self.song.selected_scene.index].clip
        automated_device = self.get_device_from_enum(self.parameter_enum.device_enum)
        if automated_device is None:
            self.parent.log_error("The automated device was not inserted")
            return None

        automated_parameter = automated_device.get_parameter_by_name(self.parameter_enum)

        existing_envelope = clip.automation_envelope(automated_parameter)
        if not existing_envelope:
            clip.create_automation_envelope(parameter=automated_parameter)

        clip.loop_end = self.clip_bar_length

        self.parent.uiManager.show_clip_envelope_parameter(clip, automated_parameter)
        if self.song.is_playing:
            clip.fire()
