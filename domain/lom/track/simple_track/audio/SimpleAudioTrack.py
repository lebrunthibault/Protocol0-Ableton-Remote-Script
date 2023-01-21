from functools import partial
from os.path import basename

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
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SimpleAudioTrack(SimpleTrack):
    CLIP_SLOT_CLASS = AudioClipSlot

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(SimpleAudioTrack, self).__init__(*a, **k)
        # this mapping makes it possible to keep the midi hash of a clip
        # even when moving it around / duplicating
        # it is shared between with the mathing track
        self.file_path_mapping = {}  # type: Dict[str, int]
        # don't flatten when the track did not change since last flatten (used to retry on error)
        self._needs_flattening = True

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
        self._needs_flattening = True

    def has_same_clips(self, track):
        # type: (SimpleAudioTrack) -> bool
        return all(clip.matches(other_clip) for clip, other_clip in zip(self.clips, track.clips))

    def set_clip_midi_hash(self, clip, midi_hash):
        # type: (AudioClip, int) -> None
        self.file_path_mapping[clip.file_path] = midi_hash
        self.data.save()

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

        seq = Sequence()
        if self._needs_flattening:
            seq.add(super(SimpleAudioTrack, self).flatten)
        seq.add(partial(self._post_flatten, clip_infos))

        return seq.done()

    def _post_flatten(self, clip_infos):
        # type: (SimpleAudioTrackClips) -> Optional[Sequence]
        flattened_track = Song.selected_track(SimpleAudioTrack)
        flattened_track._needs_flattening = False

        clip_info_by_index = {c.index: c for c in clip_infos}

        clip_infos.hydrate(flattened_track.clips)

        for clip in flattened_track.clips:
            if clip.index in clip_info_by_index:
                clip_info = clip_info_by_index[clip.index]
                midi_hash = self.file_path_mapping.get(clip_info.file_path, None)
                flattened_track.set_clip_midi_hash(clip, midi_hash)

        return flattened_track.matching_track.broadcast_clips(clip_infos, self)

    def replace_clip_sample(self, dest_track, dest_cs, source_cs=None, file_path=None):
        # type: (SimpleAudioTrack, AudioClipSlot, AudioClipSlot, str) -> Optional[Sequence]
        assert source_cs is not None or file_path is not None, "provide clip_slot or file path"

        Logger.info(
            "Replacing clip: %s-> %s"
            % (basename(dest_cs.clip.file_path), basename(file_path or source_cs.clip.file_path))
        )

        device_params = dest_track.devices.parameters
        automated_params = dest_cs.clip.automation.get_automated_parameters(device_params)

        assert source_cs is not None or file_path is not None, "provide clip_slot or file path"

        # duplicate when no automation else manual action is needed
        if len(automated_params) == 0 and source_cs is not None:
            return dest_cs.replace_clip_sample(source_cs)
        else:
            if source_cs is not None:
                file_path = source_cs.clip.file_path

            return dest_cs.replace_clip_sample(None, file_path)

    def back_to_previous_clip_file_path(self, clip):
        # type: (AudioClip) -> Sequence
        clip_slot = self.clip_slots[clip.index]

        if clip.previous_file_path is None:
            raise Protocol0Warning("No previous file path")
        elif clip.previous_file_path == clip.file_path:
            raise Protocol0Warning("file path didn't not change")

        seq = Sequence()
        seq.add(
            partial(
                self.replace_clip_sample,
                self,
                clip_slot,
                file_path=clip_slot.clip.previous_file_path,
            )
        )
        seq.add(Backend.client().close_samples_windows)
        seq.add(partial(Backend.client().show_success, "file path restored"))

        return seq.done()

    def disconnect(self):
        # type: () -> None
        self.data.save()

        super(SimpleAudioTrack, self).disconnect()
