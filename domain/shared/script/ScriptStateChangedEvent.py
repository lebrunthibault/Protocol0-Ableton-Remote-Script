class ScriptStateChangedEvent(object):
    def __init__(self, enabled):
        # type: (bool) -> None
        self.enabled = enabled
