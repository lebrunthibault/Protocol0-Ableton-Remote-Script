from typing import Any

from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class InstrumentBusTrack(SimpleAudioTrack):
    TRACK_NAME = "Instrument bus"

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(InstrumentBusTrack, self).__init__(*a, **k)
        if len(self.clips) == 0:
            raise Protocol0Error("Cannot find template dummy clip on instrument bus track")

    @property
    def template_dummy_clip_slot(self):
        # type: () -> AudioClipSlot
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
        super(InstrumentBusTrack, self).on_scenes_change()
        for clip in self.clips[1:]:
            Scheduler.defer(clip.delete)
