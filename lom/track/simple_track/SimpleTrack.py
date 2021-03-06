import Live
from typing import List, Optional

from _Framework.SubjectSlot import subject_slot
from _Framework.Util import find_if
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.clip.ClipType import ClipType
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.simple_track.SimpleTrackActionMixin import SimpleTrackActionMixin
from a_protocol_0.utils.decorators import defer


class SimpleTrack(SimpleTrackActionMixin, AbstractTrack):
    def __init__(self, track, index, *a, **k):
        # type: (Live.Track.Track, int) -> None
        self._track = track
        self.index = index
        super(SimpleTrack, self).__init__(track=self, *a, **k)
        if self.group_track:
            self.group_track.sub_tracks.append(self)
        self.linked_track = None  # type: Optional[SimpleTrack]
        self._playing_slot_index_listener.subject = self._track
        self.instrument = self.parent.deviceManager.make_instrument_from_simple_track(track=self)
        if self.is_midi:  # could later create a SimpleMidiTrack class if necessary
            self.push2_selected_matrix_mode = 'note'
            self.push2_selected_instrument_mode = 'split_melodic_sequencer'

        # only used for automated tracks
        self.next_automated_audio_track = None  # type: Optional[SimpleTrack]
        self.previous_automated_audio_track = None  # type: Optional[SimpleTrack]
        self.clip_slots = [ClipSlot.make(clip_slot=clip_slot, index=index, track=self) for (index, clip_slot) in
                           enumerate(list(self._track.clip_slots))]

        self.last_clip_played = None  # type: Optional[Clip]

    def __hash__(self):
        return self.index

    @subject_slot("playing_slot_index")
    @defer
    def _playing_slot_index_listener(self):
        # type: () -> None
        # handle one shot clips
        if self.playable_clip and self.playable_clip.type == ClipType.ONE_SHOT:
            if not self.last_clip_played or self.last_clip_played == self.playable_clip:
                self.parent.wait_beats(self.playable_clip.length, self.stop)
            else:
                self.parent.wait_beats(self.playable_clip.length, self.last_clip_played.play)

        # update track name
        if self.playing_slot_index >= 0 or any([track.is_playing for track in self.song.simple_tracks]):
            self.track_name.set(playing_slot_index=self.playing_slot_index)
        [setattr(clip, "is_selected", False) for clip in self.clips]

        self.last_clip_played = self.playable_clip if self.playing_slot_index >= 0 else None

        # noinspection PyUnresolvedReferences
        self.notify_playing_slot_index()

    @property
    def playing_slot_index(self):
        return self._track.playing_slot_index

    @property
    def is_playing(self):
        # type: () -> bool
        # return bool(self.playable_clip) and self.playable_clip.is_playing
        return any([clip_slot.is_playing for clip_slot in self.clip_slots])

    @property
    def is_triggered(self):
        # type: () -> bool
        return any([clip_slot.is_triggered for clip_slot in self.clip_slots])

    @property
    def is_recording(self):
        # type: () -> bool
        return any([clip for clip in self.clips if clip.is_recording])

    @property
    def playable_clip(self):
        # type: () -> Optional[Clip]
        selected_clip = find_if(lambda clip: clip.is_selected, self.clips)
        if selected_clip:
            return selected_clip

        index = self.playing_slot_index if self.playing_slot_index >= 0 else self.track_name.playing_slot_index
        if self.track_name.playing_slot_index >= 0 and self.clip_slots[index].has_clip:
            return self.clip_slots[index].clip
        else:
            return None

    @property
    def arm(self):
        # type: () -> bool
        return self.can_be_armed and self._track.arm

    @arm.setter
    def arm(self, arm):
        # type: (bool) -> None
        if self.can_be_armed:
            self._track.arm = arm

    @property
    def _empty_clip_slots(self):
        # type: () -> List[ClipSlot]
        return [clip_slot for clip_slot in self.clip_slots if not clip_slot.has_clip]

    @property
    def _next_empty_clip_slot_index(self):
        # type: () -> int
        index = None
        if len(self.clips):
            index = next(iter([cs.index for cs in self._empty_clip_slots if cs.index > self.clips[-1].index]), None)
        elif len(self._empty_clip_slots):
            index = self._empty_clip_slots[0].index

        if index:
            return index
        else:
            # todo: this is not sync
            self.song.create_scene()
            return len(self.song.scenes) - 1

    def disconnect(self):
        super(SimpleTrack, self).disconnect()
        [clip_slot.disconnect() for clip_slot in self.clip_slots]
        if self.instrument:
            self.instrument.disconnect()
