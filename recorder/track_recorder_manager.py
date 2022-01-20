from functools import partial

from typing import Optional, Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.components.UtilsManager import UtilsManager
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.interface.InterfaceState import InterfaceState
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.recorder.track_recorder_factory.abstract_track_recorder_factory import AbstractTrackRecorderFactory
from protocol0.recorder.track_recorder_interface import TrackRecorderInterface
from protocol0.sequence.Sequence import Sequence


class TrackRecorderManager(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderManager, self).__init__(*a, **k)
        self._audio_effect_rack_cache = {}
        self.recorder = None  # type: Optional[TrackRecorderInterface]

    @property
    def track(self):
        # type: () -> Optional[AbstractTrack]
        return self.recorder.track

    def record_track(self, track, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        if self.recorder:
            self.recorder.on_record_cancelled()
            self._cancel_record()
            return None

        self.recorder = AbstractTrackRecorderFactory.create_track_recorder(track=track, record_type=record_type, bar_length=InterfaceState.SELECTED_RECORDING_BAR_LENGTH)

        bar_length = InterfaceState.SELECTED_RECORDING_BAR_LENGTH.int_value
        if record_type == RecordTypeEnum.AUDIO_ONLY and isinstance(track, ExternalSynthTrack):
            bar_length = track.midi_track.clip_slots[self.song.selected_scene.index].clip.bar_length

        self.parent.show_message(UtilsManager.get_recording_length_legend(bar_length))

        self.song.session_automation_record = True
        self.track.has_monitor_in = False
        seq = Sequence()
        seq.add(self._arm_track)
        seq.add(self.song.check_midi_recording_quantization)

        seq.add(lambda: self.parent.log_dev("pre record"))
        seq.add(self.recorder.pre_record)
        seq.add(lambda: self.parent.log_dev("record"))
        seq.add(partial(self.recorder.record, bar_length=bar_length))
        seq.add(lambda: self.parent.log_dev("post record"))
        seq.add(self.recorder.post_record)

        seq.add(self._post_record)
        return seq.done()

    def _arm_track(self):
        # type: () -> Optional[Sequence]
        seq = Sequence()
        if not self.track.is_armed:
            if len(self.song.armed_tracks) != 0:
                options = ["Arm current track", "Record on armed track"]
                seq.select("The current track is not armed", options=options)
                seq.add(lambda: self.track.arm() if seq.res == options[0] else self.song.armed_tracks[0].select())
            else:
                seq.add(self.track.arm)

        return seq.done()

    def _cancel_record(self):
        # type: () -> None
        self.parent.clear_tasks()
        self.track.stop(immediate=True)
        self.song.stop_playing()
        self._post_record()

    def _post_record(self):
        # type: () -> None
        """ overridden """
        self.track.has_monitor_in = False
        self.track.solo = False
        self.recorder = None
