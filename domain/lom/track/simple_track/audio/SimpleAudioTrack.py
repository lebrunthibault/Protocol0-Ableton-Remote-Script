from functools import partial

import Live
from _Framework.CompoundElement import subject_slot_group
from typing import List, cast, Any, Optional, Dict

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrackClips import (
    SimpleAudioTrackClips,
)
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils.list import find_if
from protocol0.infra.persistence.TrackData import TrackData
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class SimpleAudioTrack(SimpleTrack):
    CLIP_SLOT_CLASS = AudioClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)
        # this mapping makes it possible to keep the midi hash of a clip
        # even when moving it around / duplicating
        self._file_path_mapping = {}  # type: Dict[str, int]

        self.data = TrackData(self)
        self.data.restore()

        self._has_clip_listener.replace_subjects(self._track.clip_slots)

    @property
    def clip_slots(self):
        # type: () -> List[AudioClipSlot]
        return cast(List[AudioClipSlot], super(SimpleAudioTrack, self).clip_slots)

    @property
    def clips(self):
        # type: () -> List[AudioClip]
        return super(SimpleAudioTrack, self).clips  # noqa

    @subject_slot_group("has_clip")
    def _has_clip_listener(self, _):
        # type: (Live.ClipSlot.ClipSlot) -> None
        for clip in self.clips:
            if clip.midi_hash is None and clip.file_path in self._file_path_mapping:
                self.set_clip_midi_hash(clip, self._file_path_mapping[clip.file_path])

    def has_same_clips(self, track):
        # type: (SimpleAudioTrack) -> bool
        return all(clip.matches(other_clip) for clip, other_clip in zip(self.clips, track.clips))

    def set_clip_midi_hash(self, clip, midi_hash):
        # type: (AudioClip, int) -> None
        self._file_path_mapping[clip.file_path] = midi_hash
        clip.midi_hash = midi_hash
        self.data.save()
        from protocol0.shared.logging.Logger import Logger
        Logger.dev("set clip midi hash of %s : %s" % (clip, midi_hash))

    def load_full_track(self):
        # type: () -> Sequence
        assert isinstance(Song.current_track(), SimpleAudioTrack), "Track already loaded"
        matching_track = find_if(
            lambda t: t != self and t.name == self.name and not t.is_foldable,
            Song.simple_tracks(),
        )
        if matching_track is not None:
            matching_track.select()
            raise Protocol0Warning("Track already loaded")

        track_color = self.color
        seq = Sequence()
        seq.add(self.focus)
        seq.add(Backend.client().drag_matching_track)
        seq.wait_for_backend_event("track_focused")
        seq.add(partial(setattr, self, "color", track_color))
        seq.wait_for_backend_event("matching_track_loaded")
        seq.add(partial(Backend.client().show_success, "I LOVE YOU <3"))
        return seq.done()

    def flatten(self):
        # type: () -> Sequence
        clip_infos = SimpleAudioTrackClips.make_from_track(self)
        from protocol0.shared.logging.Logger import Logger

        Logger.dev(clip_infos)

        seq = Sequence()
        seq.add(super(SimpleAudioTrack, self).flatten)
        seq.add(partial(self._post_flatten, clip_infos))

        return seq.done()

    def _post_flatten(self, clip_infos):
        # type: (SimpleAudioTrackClips) -> Optional[Sequence]
        flattened_track = Song.selected_track(SimpleAudioTrack)

        clip_infos.hydrate(flattened_track.clips)

        clip_info_by_index = {c.index: c for c in clip_infos}
        from protocol0.shared.logging.Logger import Logger
        Logger.dev(clip_info_by_index)
        for clip in flattened_track.clips:
            Logger.dev((clip, clip.index))
            if clip.index in clip_info_by_index:
                clip_info = clip_info_by_index[clip.index]
                flattened_track.set_clip_midi_hash(clip, clip_info.midi_hash)

        return flattened_track.matching_track.broadcast_clips(clip_infos)
