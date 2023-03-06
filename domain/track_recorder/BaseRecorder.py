from typing import cast

from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.event.RecordStartedEvent import RecordStartedEvent
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class BaseRecorder(object):
    """Common recording operations"""

    def __init__(self, track, record_config):
        # type: (AbstractTrack, RecordConfig) -> None
        self._track = track
        self.config = record_config

    def pre_record(self):
        # type: () -> Sequence
        seq = Sequence()
        seq.add(self._arm_track)
        seq.add(self._prepare_clip_slots_for_record)
        return seq.done()

    def _prepare_clip_slots_for_record(self):
        # type: () -> Sequence
        """isolating this, we need clip slots to be computed at runtime (if the track changes)"""
        seq = Sequence()
        seq.add([clip_slot.prepare_for_record for clip_slot in self.config.clip_slots])
        return seq.done()

    def _arm_track(self):
        # type: () -> Sequence
        seq = Sequence()
        if (
            not Song.current_track().arm_state.is_armed
            and len(list(Song.armed_tracks())) != 0
        ):
            options = ["Arm current track", "Record on armed track"]
            seq.select("The current track is not armed", options=options)
            seq.add(
                lambda: self._track.arm_state.arm()
                if seq.res == options[0]
                else setattr(self, "_track", list(Song.armed_tracks())[0])
            )
        else:
            seq.add(self._track.arm_state.arm)

        return seq.done()

    def record(self):
        # type: () -> Sequence
        # launch the record
        DomainEventBus.emit(RecordStartedEvent(
            self.config.scene_index,
            full_record=self.config.bar_length == 0,
            has_count_in=self.config.records_midi
        ))
        seq = Sequence()
        bar_length = cast(float, self.config.bar_length)
        if bar_length != 0:
            if not Song.is_playing():
                seq.wait_for_event(SongStartedEvent)
            if not self.config.records_midi:
                # play well with the tail recording
                bar_length -= 0.6

            # this works because the method is called before the beginning of the bar
            seq.wait_bars(bar_length)
            seq.wait_for_event(Last32thPassedEvent)
        else:
            seq.wait_for_event(SongStoppedEvent)
            seq.add(lambda: Song.selected_scene().scene_name.update(""))

        return seq.done()

    def cancel_record(self):
        # type: () -> None
        for clip_slot in self.config.clip_slots:
            clip_slot.delete_clip()
        self._track.stop(immediate=True)
