from protocol0.shared.logging.Logger import Logger


class SceneFiredEvent(object):
    """Event emitted **before** the scene starts playing"""
    def __init__(self, scene_index):
        # type: (int) -> None
        Logger.dev("scene fired event emitted, scene_index: %s" % scene_index)
        self.scene_index = scene_index
