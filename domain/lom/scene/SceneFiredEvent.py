import Live


class SceneFiredEvent(object):
    def __init__(self, live_scene):
        # type: (Live.Scene.Scene) -> None
        self.live_scene = live_scene
