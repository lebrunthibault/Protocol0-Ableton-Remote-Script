from functools import partial

from typing import cast

from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstractMatchingTrack import AbstractMatchingTrack
from protocol0.domain.lom.track.group_track.ext_track.ExtMonitoringState import (
    ExtMonitoringState,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class ExtMatchingTrack(AbstractMatchingTrack):
    def __init__(self, base_track):
        # type: (SimpleAudioTrack) -> None
        super(ExtMatchingTrack, self).__init__(base_track)
        self._midi_track = cast(SimpleMidiTrack, base_track.sub_tracks[0])
        self._audio_track = cast(SimpleAudioTrack, base_track.sub_tracks[1])

    def update(self, observable):
        # type: (Observable) -> None
        if isinstance(observable, ExtMonitoringState):
            self._track.monitoring_state.switch()

    def bounce(self, track_crud_component):
        # type: (TrackCrudComponent) -> Sequence
        self._assert_valid_track_name()

        if len(list(self._base_track.devices)) != 0:
            raise Protocol0Warning("Please move devices to audio track")

        self._audio_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        seq = Sequence()

        if self._track is None or not liveobj_valid(self._track._track):
            mixer_data = self._base_track.devices.mixer_device.to_dict()
            self._base_track.reset_mixer()
            seq.add(self._base_track.save)
            seq.add(self._audio_track.flatten)

            insert_index = self._base_track.sub_tracks[-1].index + 1
            seq.add(partial(track_crud_component.create_audio_track, insert_index))
            seq.add(lambda: setattr(Song.selected_track(), "name", self._base_track.name))
            seq.add(lambda: setattr(Song.selected_track(), "color", self._base_track.color))
            seq.add(
                lambda: Song.selected_track().devices.mixer_device.update_from_dict(mixer_data)
            )  # noqa
            seq.add(self._init)  # connect to the matching track

            seq.add(self._copy_clips_from_base_track)
        else:
            # seq.add(self._base_track.save)
            seq.add(self._audio_track.flatten)

        # seq.add(self._base_track.delete)
        # seq.add(partial(Backend.client().show_success, "Track bounced"))

        return seq.done()

    def _copy_clips_from_base_track(self):
        # type: () -> None
        """Copy audio clips from ext track to audio matching track"""
        audio_track = cast(SimpleAudioTrack, self._base_track.sub_tracks[1])

        for source_cs in audio_track.clip_slots:
            if source_cs.clip is None:
                continue

            source_cs.clip.muted = False
            source_cs.clip.looping = True

            destination_cs = self._track.clip_slots[source_cs.index]
            source_cs.duplicate_clip_to(destination_cs)
