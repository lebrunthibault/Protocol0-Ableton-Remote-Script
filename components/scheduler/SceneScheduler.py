from protocol0.components.scheduler.BeatScheduler import BeatScheduler
from protocol0.lom.Scene import Scene


class SceneScheduler(BeatScheduler):
    def _on_beat_changed(self):
        # type: () -> None
        if Scene.PLAYING_SCENE and Scene.PLAYING_SCENE.has_playing_clips:
            self.parent.defer(Scene.PLAYING_SCENE.on_beat_changed)
