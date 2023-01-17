from typing import Any, Optional

from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.instrument.preset.SampleSelectedEvent import SampleSelectedEvent
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger


class InstrumentBusTrack(SimpleAudioTrack):
    TRACK_NAME = "Instrument bus"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentBusTrack, self).__init__(*a, **k)
        if not self.template_dummy_clip_slot:
            raise Protocol0Error("Cannot find template dummy clip on instrument bus track")

    @property
    def template_dummy_clip_slot(self):
        # type: () -> Optional[AudioClipSlot]
        if self.clip_slots[0].clip is None:
            Logger.warning("Cannot find template dummy clip on instrument bus track")
            return None
        else:
            return self.clip_slots[0]

    def on_added(self):
        # type: () -> None
        """Template dummy clip should always be muted"""
        super(InstrumentBusTrack, self).on_added()
        if len(self.clips):
            self.clips[0].muted = True

    def on_scenes_change(self):
        # type: () -> None
        """Don't copy the template dummy clip on duplicate scene"""
        has_template_dummy_clip = self.template_dummy_clip_slot is not None
        super(InstrumentBusTrack, self).on_scenes_change()

        if has_template_dummy_clip and self.template_dummy_clip_slot is None:
            self._load_dummy_clip()

        for clip in self.clips[1:]:
            Scheduler.defer(clip.delete)

    def _load_dummy_clip(self):
        # type: () -> None
        self.select_clip_slot(self.clip_slots[0])
        DomainEventBus.emit(SampleSelectedEvent("dummy clip.wav"))
        Backend.client().show_info("Loaded dummy clip")
