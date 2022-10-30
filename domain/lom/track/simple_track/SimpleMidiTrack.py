from functools import partial

from typing import List, cast

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
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

    def on_added(self):
        # type: () -> Sequence
        matching_audio_track = find_if(
            lambda t: t.name == self.name, SongFacade.simple_tracks(SimpleAudioTrack)
        )

        seq = Sequence()
        seq.add(self.arm_state.arm)
        if matching_audio_track is not None:
            seq.add(partial(self._connect_main_track, matching_audio_track))

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

        if len(self.clips) != len(track.clips):
            return False

        for index, clip in enumerate(self.clips):
            other_clip = track.clips[index]

            if clip.hash() != other_clip.hash():
                return False

        return True
