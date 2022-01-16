from functools import partial

from typing import Optional, Any

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.config import Config
from protocol0.enums.RecordTypeEnum import RecordTypeEnum
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.sequence.Sequence import Sequence


class TrackRecorderComponent(AbstractControlSurfaceComponent):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderComponent, self).__init__(*a, **k)
        self._audio_effect_rack_cache = {}

    def record_track(self, track, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        seq = Sequence()
        seq.add(partial(self.pre_record, track=track, record_type=record_type))

        # todo : create a recorder

        return seq.done()

    def pre_record(self, track, record_type):
        # type: (AbstractTrack, RecordTypeEnum) -> Optional[Sequence]
        seq = Sequence()
        if not track.is_armed:
            if len(self.song.armed_tracks) != 0:
                options = ["Arm current track", "Record on armed track"]
                seq.select("The current track is not armed", options=options)
                seq.add(lambda: track.arm() if seq.res == options[0] else self.song.armed_tracks[0].select())
            else:
                seq.add(track.arm)

        seq.add(self.song.check_midi_recording_quantization)

        seq.add(partial(self.session_record, record_type=record_type))
        return seq.done()
    def session_record(self, record_type):
        # type: (RecordTypeEnum) -> Optional[Sequence]
        if self.is_record_triggered and Config.CURRENT_RECORD_TYPE is not None:
            return self._cancel_record()
        Config.CURRENT_RECORD_TYPE = record_type

        seq = Sequence()
        seq.add(partial(self._pre_session_record, record_type))
        seq.add(partial(self._launch_count_in, record_type))

        if record_type == RecordTypeEnum.NORMAL:
            seq.add(self._session_record_all)
        elif record_type == RecordTypeEnum.AUDIO_ONLY:
            seq.add(self._session_record_audio_only)

        seq.add(partial(self.post_session_record, record_type))

        return seq.done()

    def _session_record_all(self):
        # type: () -> Sequence
        """ this records normally on a simple track and both midi and audio on a group track """
        raise NotImplementedError

    def _session_record_audio_only(self):
        # type: () -> None
        """ overridden """
        self.parent.log_error("session_record_audio_only not available on this track")
        return None

    def _pre_session_record(self, record_type):
        # type: (RecordTypeEnum) -> Optional[Sequence]
        """ restart audio to get a count in and recfix"""
        if not self.is_armed:
            self.parent.log_error("%s is not armed for recording" % self)
            return None

        self.song.record_mode = False
        self.song.session_automation_record = True

        seq = Sequence()
        if record_type == RecordTypeEnum.NORMAL:
            if self.next_empty_clip_slot_index is None:
                seq.add(self.song.create_scene)
                seq.add(self.arm_track)
                seq.add(partial(self._pre_session_record, record_type))
            elif self.next_empty_clip_slot_index != self.song.selected_scene.index:
                seq.add(self.song.scenes[self.next_empty_clip_slot_index].select)

        return seq.done()

    def _launch_count_in(self, record_type):
        # type: (RecordTypeEnum) -> Optional[Sequence]
        self.song.metronome = True

        if record_type == RecordTypeEnum.AUDIO_ONLY:
            return None

        self.song.stop_playing()
        assert self.next_empty_clip_slot_index is not None
        recording_scene = self.song.scenes[self.next_empty_clip_slot_index]
        self.song.stop_all_clips(quantized=False)  # stopping previous scene clips
        # solo for count in
        self.solo = True
        self.song.is_playing = True
        self.parent.wait_bars(1, partial(setattr, self, "solo", False))

        if recording_scene.length:
            seq = Sequence()
            seq.add(wait=1)
            seq.add(recording_scene.fire)
            return seq.done()
        else:
            return None

    def _cancel_record(self):
        # type: () -> Sequence
        self.parent.clear_tasks()
        seq = Sequence()
        seq.add(partial(self.delete_playable_clip))
        seq.add(partial(self.stop, immediate=True))
        seq.add(partial(self.post_session_record, Config.CURRENT_RECORD_TYPE))
        seq.add(self.song.stop_playing)
        return seq.done()

    def post_session_record(self):
        # type: () -> None
        """ overridden """
        self.has_monitor_in = False
        self.solo = False

        Config.CURRENT_RECORD_TYPE = None


