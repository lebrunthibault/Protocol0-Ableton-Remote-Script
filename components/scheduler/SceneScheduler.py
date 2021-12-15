from protocol0.components.scheduler.BeatScheduler import BeatScheduler


class SceneScheduler(BeatScheduler):
    def _on_beat_changed(self):
        # type: () -> None
        if self.song.playing_scene and self.song.playing_scene.has_playing_clips:
            self.parent.defer(self.song.playing_scene.on_beat_changed)
