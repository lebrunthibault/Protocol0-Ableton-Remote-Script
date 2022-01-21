from typing import Optional, List

from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence


class AbstractTrackRecorder(AbstractObject):
    def __init__(self, track):
        # type: (AbstractTrack) -> None
        super(AbstractTrackRecorder, self).__init__()
        self.track = track
        self._recording_scene_index = None  # type: Optional[int]

    @property
    def recording_scene_index(self):
        # type: () -> int
        assert self._recording_scene_index is not None
        return self._recording_scene_index

    def set_recording_scene_index(self, recording_scene_index):
        # type: (int) -> None
        self._recording_scene_index = recording_scene_index

    def arm_track(self):
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

    def pre_record(self):
        # type: () -> Optional[Sequence]
        self.song.session_automation_record = True
        self.track.has_monitor_in = False
        return self._pre_record()

    def _pre_record(self):
        # type: () -> Optional[Sequence]
        pass

    def record(self, bar_length):
        # type: (int) -> Sequence
        seq = Sequence()
        seq.add([clip_slot.record for clip_slot in self._recording_clip_slots])
        return seq.done()

    @property
    def _recording_clip_slots(self):
        # type: () -> List[ClipSlot]
        return [track.clip_slots[self.recording_scene_index] for track in self._recording_tracks]

    @property
    def _recording_tracks(self):
        # type: () -> List[SimpleTrack]
        raise NotImplementedError

    def post_record(self, errored=False):
        # type: (bool) -> None
        self.song.metronome = False
        self.track.has_monitor_in = False
        if not errored:
            self.song.selected_scene.fire()
            self._post_record()

    def _post_record(self):
        # type: () -> None
        pass

    def cancel_record(self):
        # type: () -> None
        for clip_slot in self._recording_clip_slots:
            clip_slot.delete_clip()
        self.parent.clear_tasks()
        self.track.stop(immediate=True)
        self.song.stop_playing()
        self.post_record(errored=True)
