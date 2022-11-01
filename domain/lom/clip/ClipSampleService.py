from os.path import basename

from typing import List

from protocol0.domain.lom.clip.AudioClipCreatedEvent import AudioClipCreatedEvent
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.ui.ColorEnum import ColorEnum
from protocol0.domain.track_recorder.external_synth.ClipToReplaceDetectedEvent import \
    ClipToReplaceDetectedEvent
from protocol0.shared.logging.Logger import Logger


class ClipToReplace(object):
    def __init__(self, track, clip_slot, file_path):
        # type: (SimpleAudioTrack, AudioClipSlot, str) -> None
        self._track = track
        self._clip_slot = clip_slot
        self._clip = clip_slot.clip
        self._file_path = basename(file_path)

    def __repr__(self):
        # type: () -> str
        return "ClipToReplace(%s, %s)" % (self._clip, self._file_path)

    def exists(self):
        # type: () -> bool
        return liveobj_valid(self._clip._clip)

    def mark(self):
        # type: () -> None
        self._clip.appearance.color = ColorEnum.WARNING.color_int_value

    def prepare_for_replacement(self):
        # type: () -> None
        Backend.client().search(self._file_path)
        Logger.info("Replace clip with '%s'" % self._file_path)
        self._track.select_clip_slot(self._clip_slot._clip_slot)
        Logger.dev(self._clip_slot.clip.loop.start)

        self._clip_slot.mark_as_replaceable()


class ClipSampleService(object):
    def __init__(self):
        # type: () -> None
        self._clips_to_replace = []  # type: List[ClipToReplace]

        DomainEventBus.subscribe(ClipToReplaceDetectedEvent, self._on_clip_to_replace_detected_event)
        DomainEventBus.subscribe(AudioClipCreatedEvent, self._on_audio_clip_created_event)

    def reset_clips_to_replace(self):
        # type: () -> None
        self._clips_to_replace = []

    def _on_clip_to_replace_detected_event(self, event):
        # type: (ClipToReplaceDetectedEvent) -> None
        self._clips_to_replace.append(event.clip_to_replace)
        event.clip_to_replace.mark()

        if len(self._clips_to_replace) == 1:
            self._clips_to_replace[0].prepare_for_replacement()

    def _on_audio_clip_created_event(self, _):
        # type: (AudioClipCreatedEvent) -> None
        clips_count = len(self._clips_to_replace)
        if clips_count == 0:
            return

        self._clips_to_replace = filter(lambda c: c.exists(), self._clips_to_replace)

        if len(self._clips_to_replace) == 0:
            Backend.client().show_success("All clips replaced !")
            return

        # check a clip has been replaced
        if len(self._clips_to_replace) == clips_count:
            return

        next_clip = next(iter(self._clips_to_replace), None)

        if next_clip:
            next_clip.prepare_for_replacement()
            Logger.info("Still %s clips to replace" % len(self._clips_to_replace))
