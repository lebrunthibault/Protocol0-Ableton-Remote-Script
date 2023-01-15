from functools import partial

from typing import Optional, cast

from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.abstract_track.AbstractMatchingTrack import AbstractMatchingTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthMatchingTrack(AbstractMatchingTrack):
    def __init__(self, base_track, midi_track):
        # type: (SimpleAudioTrack, SimpleMidiTrack) -> None
        super(ExternalSynthMatchingTrack, self).__init__(base_track)
        self._base_midi_track = midi_track

    def connect_base_track(self):
        # type: () -> None
        # keep editor on only on a new track
        if self._track is None and self._base_midi_track.instrument is not None:
            self._base_midi_track.instrument.force_show = True

        if self._track is None:
            return

        super(ExternalSynthMatchingTrack, self).connect_base_track()
        self._connect_main_track()

    def _connect_main_track(self, show_midi_clip=True):
        # type: (bool) -> Optional[Sequence]
        if not show_midi_clip:
            return None

        seq = Sequence()

        # select the first midi clip
        first_cs = next((cs for cs in self._base_midi_track.clip_slots if cs.clip), None)
        if first_cs is not None:
            self._base_midi_track.select_clip_slot(first_cs)

        instrument = self._base_midi_track.instrument
        if instrument is not None and instrument.needs_exclusive_activation:
            seq.wait(20)  # wait for editor activation

        seq.add(ApplicationViewFacade.show_clip)
        if first_cs is not None:
            seq.defer()
            seq.add(first_cs.clip.show_notes)

        return seq.done()

    def bounce(self, track_crud_component):
        # type: (TrackCrudComponent) -> Sequence
        if len(self._base_track.clips) == 0:
            raise Protocol0Warning("No atk clip, please record first")

        self._assert_valid_track_name()

        seq = Sequence()

        if self._track is None or not liveobj_valid(self._track._track):
            seq.add(
                partial(
                    track_crud_component.create_audio_track,
                    self._base_track.sub_tracks[-1].index + 1,
                )
            )
            seq.add(lambda: setattr(SongFacade.selected_track(), "name", self._base_track.name))
            seq.add(lambda: setattr(SongFacade.selected_track(), "color", self._base_track.color))

            seq.add(self._copy_params_from_base_track)
            seq.add(self._copy_clips_from_base_track)
            seq.add(partial(Backend.client().show_success, "Track created. Bounce again."))
        else:
            seq.add(self._base_track.save)
            seq.add(self._base_track.delete)
            seq.add(partial(Backend.client().show_success, "Track bounced"))

        return seq.done()

    def _copy_clips_from_base_track(self):
        # type: () -> None
        """Copy audio clips from ext track to audio matching track"""
        audio_track = cast(SimpleAudioTrack, self._base_track.sub_tracks[1])

        if len(audio_track.clips) == 0:
            raise Protocol0Warning("Audio track has no clips")

        source_cs = audio_track.clip_slots[audio_track.clips[0].index]
        source_cs.clip.muted = False
        source_cs.clip.looping = True

        midi_clip_slots = self._base_midi_track.clip_slots
        for mcs in midi_clip_slots:
            destination_cs = self._track.clip_slots[mcs.index]
            if mcs.clip is not None and destination_cs.clip is None:
                assert source_cs.clip.looping, "audio cs not looped"

                source_cs.duplicate_clip_to(destination_cs)
