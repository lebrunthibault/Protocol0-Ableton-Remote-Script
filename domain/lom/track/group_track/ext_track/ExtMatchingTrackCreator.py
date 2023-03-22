from functools import partial

from typing import cast, Any

from protocol0.domain.lom.clip.ClipInfo import ClipInfo
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackCreatorInterface import (
    MatchingTrackCreatorInterface,
)
from protocol0.domain.lom.track.group_track.matching_track.utils import assert_valid_track_name
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class ExtMatchingTrackCreator(MatchingTrackCreatorInterface):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ExtMatchingTrackCreator, self).__init__(*a, **k)
        self._base_track = cast(SimpleAudioTrack, self._base_track)
        self._midi_track = cast(SimpleMidiTrack, self._base_track.sub_tracks[0])
        self._audio_track = cast(SimpleAudioTrack, self._base_track.sub_tracks[1])

    def bounce(self):
        # type: () -> Sequence
        assert_valid_track_name(self._base_track.name)

        if len(list(self._base_track.devices)) != 0:
            raise Protocol0Warning("Please move devices to audio track")

        # populate the mapping
        for midi_cs, audio_cs in zip(self._midi_track.clip_slots, self._audio_track.clip_slots):
            if audio_cs.clip is None:
                continue

            assert midi_cs.clip is not None, "Incoherent clip layout"

            self._audio_track.clip_mapping.register_file_path(
                audio_cs.clip.file_path, ClipInfo(midi_cs.clip, self._midi_track.devices.parameters)
            )

        self._audio_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
        # noinspection DuplicatedCode
        seq = Sequence()

        mixer_data = self._base_track.devices.mixer_device.to_dict()
        self._base_track.reset_mixer()
        seq.add(self._base_track.save)

        # noinspection DuplicatedCode
        insert_index = self._base_track.sub_tracks[-1].index + 1
        seq.add(partial(self._track_crud_component.create_audio_track, insert_index))
        seq.add(lambda: setattr(Song.selected_track(), "name", self._base_track.name))
        seq.add(lambda: setattr(Song.selected_track(), "color", self._base_track.color))
        seq.add(
            lambda: Song.selected_track().devices.mixer_device.update_from_dict(mixer_data)
        )  # noqa
        seq.add(self._audio_track.flatten)
        seq.add(self._base_track.delete)
        seq.add(partial(Backend.client().show_success, "Track bounced"))


        return seq.done()
