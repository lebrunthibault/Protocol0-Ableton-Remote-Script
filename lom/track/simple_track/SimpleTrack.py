import Live
from typing import List, Optional, Any, Dict

from _Framework.SubjectSlot import subject_slot, subject_slot_group
from a_protocol_0.enums.ClipTypeEnum import ClipTypeEnum
from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.AbstractTrack import AbstractTrack
from a_protocol_0.lom.track.simple_track.SimpleTrackActionMixin import SimpleTrackActionMixin
from a_protocol_0.utils.decorators import defer, p0_subject_slot


class SimpleTrack(SimpleTrackActionMixin, AbstractTrack):
    CLIP_CLASS = Clip

    def __init__(self, track, index, *a, **k):
        # type: (Live.Track.Track, int, Any, Any) -> None
        self._track = track  # type: Live.Track.Track
        self.index = index  # type: int
        super(SimpleTrack, self).__init__(track=self, *a, **k)
        if self.group_track:
            self.group_track.sub_tracks.append(self)
        self.linked_track = None  # type: Optional[SimpleTrack]
        self._playing_slot_index_listener.subject = self._track
        self._fired_slot_index_listener.subject = self._track
        self.instrument = self.parent.deviceManager.make_instrument_from_simple_track(track=self)
        self._instrument_listener.subject = self

        # only used for automated tracks
        self.next_automated_audio_track = None  # type: Optional[SimpleTrack]
        self.previous_automated_audio_track = None  # type: Optional[SimpleTrack]

        self.clip_slots = []  # type: List[ClipSlot]
        self.map_clip_slots()

        self.last_clip_played = None  # type: Optional[Clip]

    def __hash__(self):
        # type: () -> int
        return self.index

    def map_clip_slots(self):
        # type: () -> Any
        """ create new ClipSlot objects and keep existing ones """
        live_clip_slot_to_clip_slot = {}  # type: Dict[Live.ClipSlot.ClipSlot, ClipSlot]
        for clip_slot in self.clip_slots:
            live_clip_slot_to_clip_slot[clip_slot._clip_slot] = clip_slot
        new_clip_slots = []  # type: List[ClipSlot]
        for (i, clip_slot) in enumerate(list(self._track.clip_slots)):
            if clip_slot in live_clip_slot_to_clip_slot:
                new_clip_slots.append(live_clip_slot_to_clip_slot[clip_slot])
            else:
                new_clip_slots.append(ClipSlot.make(clip_slot=clip_slot, index=i, track=self))
        self.clip_slots = new_clip_slots
        self._map_clip_listener.replace_subjects(self.clip_slots)

    @subject_slot("playing_slot_index")
    @defer
    def _playing_slot_index_listener(self):
        # type: () -> None
        # handle one shot clips
        if self.playable_clip and self.playable_clip.type == ClipTypeEnum.ONE_SHOT:
            if not self.last_clip_played or self.last_clip_played == self.playable_clip:
                self.parent.wait_beats(self.playable_clip.length - 1, self.stop)
            else:
                self.parent.wait_beats(self.playable_clip.length - 1, self.last_clip_played.play)

        # we keep track state when the set is stopped
        if all([not track.is_playing for track in self.song.simple_tracks]):
            return

        self.last_clip_played = self.playing_clip

    @p0_subject_slot("fired_slot_index")
    def _fired_slot_index_listener(self):
        # type: () -> None
        # noinspection PyUnresolvedReferences
        self.parent.defer(self.notify_fired_slot_index)

    @p0_subject_slot("instrument")
    @defer
    def _instrument_listener(self):
        # type: () -> None
        if self.instrument:
            self.color = self.instrument.TRACK_COLOR
            if self.instrument.SHOULD_UPDATE_TRACK_NAME:
                self.track_name.update(base_name=self.instrument.NAME)

    @subject_slot_group("map_clip")
    def _map_clip_listener(self, clip_slot):
        # type: (ClipSlot) -> None
        pass

    @property
    def playing_slot_index(self):
        # type: () -> int
        return self._track.playing_slot_index

    @property
    def fired_slot_index(self):
        # type: () -> int
        return self._track.fired_slot_index

    @property
    def live_id(self):
        # type: () -> int
        return self._track._live_ptr

    @property
    def is_audio(self):
        # type: () -> bool
        from a_protocol_0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack

        return isinstance(self, SimpleAudioTrack) and self._track.has_audio_input

    @property
    def is_midi(self):
        # type: () -> bool
        from a_protocol_0.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack

        return isinstance(self, SimpleMidiTrack) and self._track.has_midi_input

    @property
    def is_playing(self):
        # type: () -> bool
        return any(clip_slot.is_playing for clip_slot in self.clip_slots)

    @property
    def is_triggered(self):
        # type: () -> bool
        return any(clip_slot.is_triggered for clip_slot in self.clip_slots)

    @property
    def is_recording(self):
        # type: () -> bool
        return any(clip for clip in self.clips if clip.is_recording)

    @property
    def playing_clip(self):
        # type: () -> Optional[Clip]
        """ Returns the currently playing clip is any """
        return self.clip_slots[self.playing_slot_index].clip if self.playing_slot_index >= 0 else None

    @property
    def playable_clip(self):
        # type: () -> Optional[Clip]
        """
            The clip preselected for playing on track play

            Checked in order :
            - The playing clip
            - The clip corresponding to the selected scene if it exists
        :return:
        """
        return self.playing_clip or self.clip_slots[self.song.selected_scene.index].clip

    @property
    def _empty_clip_slots(self):
        # type: () -> List[ClipSlot]
        return [clip_slot for clip_slot in self.clip_slots if not clip_slot.has_clip]

    @property
    def next_empty_clip_slot_index(self):
        # type: () -> Optional[int]
        for i in range(self.song.selected_scene.index, len(self.song.scenes)):
            if not self.clip_slots[i].clip:
                return i

        return None

    def disconnect(self):
        # type: () -> None
        super(SimpleTrack, self).disconnect()
        for clip_slot in self.clip_slots:
            clip_slot.disconnect()
        if self.instrument:
            self.instrument.disconnect()
