import Live


class SceneLastBarPassedEvent(object):
    def __init__(self, live_scene):
        # type: (Live.Scene.Scene) -> None
        self.live_scene = live_scene

    def target(self):
        # type: () -> object
        return self.live_scene
