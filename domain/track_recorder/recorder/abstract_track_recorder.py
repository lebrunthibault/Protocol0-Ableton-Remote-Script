from typing import Optional, List

from protocol0.domain.lom.AbstractObject import AbstractObject
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.sequence.Sequence import Sequence


class AbstractTrackRecorder(AbstractObject):
    def __init__(self, track):
        # type: (AbstractTrack) -> None
        super(AbstractTrackRecorder, self).__init__()
        self.track = track
        self._recording_scene_index = None  # type: Optional[int]

    def __repr__(self):
        # type: () -> str
        return "%s of %s" % (self.__class__.__name__, self.track)

    @property
    def recording_scene_index(self):
        # type: () -> int
        assert self._recording_scene_index is not None
        return self._recording_scene_index

    def set_recording_scene_index(self, recording_scene_index):
        # type: (int) -> None
        self._recording_scene_index = recording_scene_index

    @property
    def _recording_clip_slots(self):
        # type: () -> List[ClipSlot]
        return [track.clip_slots[self.recording_scene_index] for track in self._recording_tracks]

    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        raise NotImplementedError

    @property
    def _main_recording_track(self):
        # type: () -> SimpleTrack
        raise NotImplementedError

    def pre_record(self):
        # type: () -> Sequence
        self.song.session_automation_record = True
        seq = Sequence()
        seq.add(self.song.check_midi_recording_quantization)
        seq.add(self._arm_track)
        seq.add([clip_slot.prepare_for_record for clip_slot in self._recording_clip_slots])
        seq.add(self._pre_record)
        return seq.done()

    def _arm_track(self):
        # type: () -> Sequence
        seq = Sequence()
        if not self.track.is_armed:
            if len(self.song.armed_tracks) != 0:
                options = ["Arm current track", "Record on armed track"]
                seq.select("The current track is not armed", options=options)
                seq.add(lambda: self.track.arm() if seq.res == options[0] else self.song.armed_tracks[0].select())
            else:
                seq.add(self.track.arm)

        return seq.done()

    def _pre_record(self):
        # type: () -> Optional[Sequence]
        pass

    def record(self, bar_length):
        # type: (int) -> Sequence
        self.song.session_record = True
        self._focus_main_clip()
        seq = Sequence()
        if bar_length:
            seq.add(wait_bars=bar_length)
        else:
            seq.add(complete_on=self.song.is_playing_listener)
        return seq.done()

    def _focus_main_clip(self):
        # type: () -> Sequence
        seq = Sequence()
        main_clip_slot = self._main_recording_track.clip_slots[self.recording_scene_index]
        if not main_clip_slot.clip:
            seq.add(complete_on=main_clip_slot.has_clip_listener)
        seq.add(lambda: main_clip_slot.clip.select())
        return seq.done()

    def post_audio_record(self):
        # type: () -> None
        self.song.metronome = False

    def post_record(self):
        # type: () -> None
        self.song.session_record = False
        self.song.session_automation_record = False
        for clip_slot in self._recording_clip_slots:
            if clip_slot.clip:
                clip_slot.clip.post_record()
        return self._post_record()

    def _post_record(self):
        # type: () -> None
        pass

    def cancel_record(self):
        # type: () -> None
        for clip_slot in self._recording_clip_slots:
            clip_slot.delete_clip()
        self.song.metronome = False
        self.track.stop(immediate=True)
        self.song.stop_playing()
