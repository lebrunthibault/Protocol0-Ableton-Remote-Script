from typing import Any

from protocol0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack


class SimpleDummyTrack(SimpleAudioTrack):
    DEFAULT_NAME = "dummy"

    def __init__(self, track, *a, **k):
        # type: (Live.Track.Track, Any, Any) -> None
        super(SimpleDummyTrack, self).__init__(track=track, *a, **k)

        self.has_monitor_in = True

        self.parent.defer(self._insert_dummy_clip)

    def _insert_dummy_clip(self):
        # type: () -> None
        if self.song.template_dummy_clip:
            self.song.template_dummy_clip.clip_slot.duplicate_clip_to(self.clip_slots[self.song.selected_scene.index])

    def _rename_track(self):
        # type: () -> None
        self.name = "dummy %s" % self