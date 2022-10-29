from functools import partial

from typing import Optional, List

from protocol0.domain.lom.clip.ClipCreatedOrDeletedEvent import ClipCreatedOrDeletedEvent
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class AbstractTrackRecorder(object):
    def __init__(self, track, playback_component, recording_component):
        # type: (AbstractTrack, PlaybackComponent, RecordingComponent) -> None
        super(AbstractTrackRecorder, self).__init__()
        self._track = track
        self._playback_component = playback_component
        self._recording_component = recording_component

        self._recording_scene_index = None  # type: Optional[int]

    @property
    def track(self):
        # type: (AbstractTrackRecorder) -> AbstractTrack
        return self._track

    def __repr__(self):
        # type: () -> str
        return "%s(track=%s)" % (self.__class__.__name__, self.track)

    def legend(self, bar_length):
        # type: (int) -> str
        return "%s bars" % str(bar_length) if bar_length else "unlimited"

    @property
    def recording_scene_index(self):
        # type: () -> int
        assert self._recording_scene_index is not None
        return self._recording_scene_index

    @property
    def recording_scene(self):
        # type: () -> Scene
        return SongFacade.scenes()[self.recording_scene_index]

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
        # type: () -> Optional[SimpleTrack]
        return None

    def pre_record(self):
        # type: () -> Sequence
        self._recording_component.session_automation_record = True
        seq = Sequence()
        seq.add(self._arm_track)
        seq.add(self._prepare_clip_slots_for_record)
        seq.add(self._pre_record)
        return seq.done()

    def _prepare_clip_slots_for_record(self):
        # type: () -> Sequence
        """isolating this, we need clip slots to be computed at runtime (if the track changes)"""
        seq = Sequence()
        seq.add([clip_slot.prepare_for_record for clip_slot in self._recording_clip_slots])
        return seq.done()

    def _arm_track(self):
        # type: () -> Sequence
        seq = Sequence()
        if (
            not SongFacade.current_track().arm_state.is_armed
            and len(list(SongFacade.armed_tracks())) != 0
        ):
            options = ["Arm current track", "Record on armed track"]
            seq.select("The current track is not armed", options=options)
            seq.add(
                lambda: self.track.arm_state.arm()
                if seq.res == options[0]
                else setattr(self, "_track", list(SongFacade.armed_tracks())[0])
            )
        else:
            seq.add(self.track.arm_state.arm)

        return seq.done()

    def _pre_record(self):
        # type: () -> None
        pass

    def record(self, bar_length):
        # type: (float) -> Sequence
        self.recording_scene.fire()
        self._recording_component.session_record = True
        # only for unlimited recordings so that we can play with other tracks as well
        if bar_length == 0:
            self._recording_component.record_mode = True

        self._focus_main_clip()
        seq = Sequence()
        if bar_length:
            if not SongFacade.is_playing():
                seq.wait_for_event(SongStartedEvent)
            seq.wait_bars(
                bar_length
            )  # this works because the method is called before the beginning of the bar
            seq.wait_for_event(Last32thPassedEvent)
        else:
            seq.wait_for_event(SongStoppedEvent)
            seq.add(lambda: SongFacade.selected_scene().scene_name.update(""))

        return seq.done()

    def _focus_main_clip(self):
        # type: () -> Optional[Sequence]
        if self._main_recording_track is None:
            return None

        seq = Sequence()
        main_clip_slot = self._main_recording_track.clip_slots[self.recording_scene_index]
        if not main_clip_slot.clip:
            seq.wait_for_event(ClipCreatedOrDeletedEvent, main_clip_slot._clip_slot)
        seq.add(lambda: self._main_recording_track.select_clip_slot(main_clip_slot._clip_slot))
        return seq.done()

    def post_audio_record(self):
        # type: () -> Optional[Sequence]
        self._playback_component.metronome = False
        self._recording_component.session_automation_record = False
        self._post_audio_record()
        return None

    def _post_audio_record(self):
        # type: () -> None
        pass

    def post_record(self, bar_length):
        # type: (int) -> Optional[Sequence]
        self._recording_component.session_record = False
        for clip_slot in self._recording_clip_slots:
            if clip_slot.clip:
                # deferring because the clip length is not accurate right now
                Scheduler.wait(10, partial(clip_slot.clip.post_record, bar_length))
        self._post_record()
        return None

    def _post_record(self):
        # type: () -> None
        pass

    def cancel_record(self):
        # type: () -> None
        for clip_slot in self._recording_clip_slots:
            clip_slot.delete_clip()
        self._playback_component.metronome = False
        self.track.stop(immediate=True)
