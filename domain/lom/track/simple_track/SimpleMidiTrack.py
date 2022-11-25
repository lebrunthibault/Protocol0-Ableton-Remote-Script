from functools import partial

from typing import List, cast, Optional

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence


class SimpleMidiTrack(SimpleTrack):
    CLIP_SLOT_CLASS = MidiClipSlot

    @property
    def clip_slots(self):
        # type: () -> List[MidiClipSlot]
        return cast(List[MidiClipSlot], super(SimpleMidiTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[MidiClip]
        return super(SimpleMidiTrack, self).clips  # noqa

    def _get_matching_track(self):
        # type: () -> Optional[SimpleAudioTrack]
        return find_if(
            lambda t: not t.is_foldable and t.name == self.name,
            SongFacade.simple_tracks(SimpleAudioTrack),
        )

    def on_added(self):
        # type: () -> Sequence
        matching_track = self._get_matching_track()

        seq = Sequence()
        seq.add(self.arm_state.arm)
        if matching_track is not None:
            seq.add(partial(self._connect_main_track, matching_track))

        return seq.done()

    def _connect_main_track(self, matching_audio_track):
        # type: (SimpleAudioTrack) -> Sequence
        # plug the external synth recording track in its main audio track
        seq = Sequence()
        matching_audio_track.current_monitoring_state = CurrentMonitoringStateEnum.IN
        self.output_routing.track = matching_audio_track

        # select the first midi clip
        seq.add(ApplicationViewFacade.show_clip)
        if len(self.clips) != 0:
            seq.defer()
            seq.add(self.clips[0].show_notes)

        return seq.done()

    def has_same_clips(self, track):
        # type: (AbstractTrack) -> bool
        if not isinstance(track, SimpleMidiTrack):
            return False

        return all(clip.matches(other_clip) for clip, other_clip in zip(self.clips, track.clips))

    def duplicate_selected_clip(self):
        # type: () -> Sequence
        selected_cs = SongFacade.selected_clip_slot(MidiClipSlot)
        clip = selected_cs.clip
        if clip is None:
            raise Protocol0Warning("No selected clip")

        matching_clip_slots = [c for c in self.clip_slots if c.clip and c.clip.matches(clip) and c.clip is not clip]

        seq = Sequence()
        seq.add([partial(selected_cs.duplicate_clip_to, cs) for cs in matching_clip_slots])
        return seq.done()

    def _on_disconnect_matching_track(self):
        # type: () -> None
        """Restore the current monitoring state of the main track"""
        matching_track = self._get_matching_track()
        if matching_track is not None:
            matching_track.current_monitoring_state = CurrentMonitoringStateEnum.AUTO

    def disconnect(self):
        # type: () -> None
        super(SimpleMidiTrack, self).disconnect()
        if not self._track:
            Scheduler.defer(self._on_disconnect_matching_track)
