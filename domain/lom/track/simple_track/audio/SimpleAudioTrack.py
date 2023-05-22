from functools import partial
from os.path import basename

import Live
from _Framework.CompoundElement import subject_slot_group
from typing import List, cast, Any, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.simple_track.AudioToMidiClipMapping import AudioToMidiClipMapping
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
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
        # don't flatten when the track did not change since last flatten (used to retry on error)
        self._needs_flattening = True

        self._data = TrackData(self)
        self.clip_mapping = AudioToMidiClipMapping(self._data)
        self._data.restore()

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
        seq.wait_for_event(TracksMappedEvent)
        seq.add(partial(Backend.client().close_explorer_window, "tracks"))
        seq.add(partial(Backend.client().show_success, "Track loaded"))
        return seq.done()

    def flatten(self, flatten_track=True):
        # type: (bool) -> Sequence
        return super(SimpleAudioTrack, self).flatten(self._needs_flattening)

    def replace_clip_sample(self, dest_cs, source_cs=None, file_path=None):
        # type: (AudioClipSlot, AudioClipSlot, str) -> Optional[Sequence]
        assert source_cs is not None or file_path is not None, "provide clip_slot or file path"

        Logger.info(
            "Replacing clip: %s-> %s"
            % (basename(dest_cs.clip.file_path), basename(file_path or source_cs.clip.file_path))
        )

        device_params = self.devices.parameters
        automated_params = dest_cs.clip.automation.get_automated_parameters(device_params)

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
        previous_file_path = clip.previous_file_path

        if previous_file_path is None:
            raise Protocol0Warning("No previous file path")
        elif previous_file_path == clip.file_path:
            raise Protocol0Warning("file path didn't not change")

        seq = Sequence()
        seq.add(partial(self.replace_clip_sample, clip_slot, file_path=previous_file_path))
        seq.add(Backend.client().close_samples_windows)
        seq.add(partial(Backend.client().show_success, "file path restored"))

        return seq.done()

    def disconnect(self):
        # type: () -> None
        self._data.save()

        super(SimpleAudioTrack, self).disconnect()
