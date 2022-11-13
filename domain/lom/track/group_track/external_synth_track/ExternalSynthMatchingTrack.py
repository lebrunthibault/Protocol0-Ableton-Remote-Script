from functools import partial

from typing import Optional, cast

from protocol0.domain.lom.clip.ClipNameEnum import ClipNameEnum
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.group_track.dummy_group.DummyGroup import DummyGroup
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrackMonitoringState import (  # noqa
    ExternalSynthTrackMonitoringState,
)
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class ExternalSynthMatchingTrack(object):
    def __init__(self, base_track, midi_track, base_dummy_group):
        # type: (SimpleAudioTrack, SimpleMidiTrack, DummyGroup) -> None
        self._base_track = base_track
        self._base_midi_track = midi_track
        self._base_dummy_group = base_dummy_group

        self._track = self._get_track()

    def _get_track(self):
        # type: () -> Optional[SimpleAudioTrack]
        return find_if(
            lambda t: not t.is_foldable and t.name == self._base_track.name,
            SongFacade.simple_tracks(SimpleAudioTrack),
        )

    def _get_atk_cs(self):
        # type: () -> Optional[AudioClipSlot]
        atk_cs = find_if(
            lambda cs: cs.clip is not None
            and cs.clip.clip_name.base_name == ClipNameEnum.ATK.value,
            self._base_track.sub_tracks[1].clip_slots,
        )
        if atk_cs is not None:
            return cast(AudioClipSlot, atk_cs)
        else:
            return find_if(
                lambda cs: cs.clip is not None
                and cs.clip.clip_name.base_name == ClipNameEnum.ONCE.value,
                self._base_track.sub_tracks[1].clip_slots,
            )

    def connect_main_track(self):
        # type: () -> None
        # keep editor on only on a new track
        if self._track is None and self._base_midi_track.instrument is not None:
            self._base_midi_track.instrument.force_show = True

        Scheduler.defer(self._connect_main_track)

    def _connect_main_track(self, show_midi_clip=True):
        # type: (bool) -> Optional[Sequence]
        # plug the external synth recording track in its main audio track
        if self._track is None:
            return None

        seq = Sequence()
        self._track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self._base_track.output_routing.track = self._track

        if not show_midi_clip:
            return None

        # select the first midi clip
        first_cs = next((cs for cs in self._base_midi_track.clip_slots if cs.clip), None)
        if first_cs is not None:
            self._base_midi_track.select_clip_slot(first_cs._clip_slot)

        instrument = self._base_midi_track.instrument
        if instrument is not None and instrument.needs_exclusive_activation:
            seq.wait(20)  # wait for editor activation

        seq.add(ApplicationViewFacade.show_clip)
        if first_cs is not None:
            seq.defer()
            seq.add(first_cs.clip.show_notes)

        return seq.done()

    def copy_from_base_track(self, track_crud_component):
        # type: (TrackCrudComponent) -> Sequence
        if self._get_atk_cs() is None:
            raise Protocol0Warning("No atk clip, please record first")

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
        seq.defer()
        seq.add(partial(self._connect_main_track, False))
        return seq.done()

    def _copy_params_from_base_track(self):
        # type: () -> None
        self._track = self._get_track()
        assert self._track, "no matching track"

        self._track.volume = self._base_track.volume
        self._base_track.volume = 0

        self._base_track.devices.mixer_device.copy_to(self._track.devices.mixer_device)
        self._base_track.devices.mixer_device.reset()

        devices = self._base_track.devices.all + list(self._base_dummy_group.devices)

        if len(devices) == 0:
            Backend.client().show_success("Track copied ! (no devices)")
            return

        self._base_track.select()
        ApplicationViewFacade.show_device()
        message = "Please copy %s devices" % len(devices)

        scenes_with_automation = [
            i for i in range(len(SongFacade.scenes())) if self._base_dummy_group.has_automation(i)
        ]
        if len(scenes_with_automation):
            message += "\nAutomation present on scenes %s" % scenes_with_automation

        Backend.client().show_info(message)

    def _copy_clips_from_base_track(self):
        # type: () -> None
        atk_cs = self._get_atk_cs()
        assert atk_cs, "No atk clip"
        atk_cs.clip.muted = False
        atk_cs.clip.looping = True

        loop_cs = None
        if len(self._base_track.sub_tracks) > 2:
            loop_cs = find_if(
                lambda cs: cs.clip is not None
                and cs.clip.clip_name.base_name == ClipNameEnum.LOOP.value,
                self._base_track.sub_tracks[2].clip_slots,
            )

        if loop_cs is not None:
            loop_cs.clip.muted = False
            loop_cs.clip.looping = True

        midi_clip_slots = self._base_midi_track.clip_slots
        for mcs in midi_clip_slots:
            main_cs = self._track.clip_slots[mcs.index]
            if mcs.clip is not None and main_cs.clip is None:
                is_loop_clip = (
                    loop_cs is not None
                    and mcs.index != 0
                    and midi_clip_slots[mcs.index - 1].clip is not None
                )
                audio_cs = loop_cs if is_loop_clip else atk_cs
                assert audio_cs.clip.looping

                audio_cs.duplicate_clip_to(main_cs)

    def disconnect_base(self):
        # type: () -> None
        """Restore the current monitoring state of the track"""
        if self._track is not None:
            self._track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO
