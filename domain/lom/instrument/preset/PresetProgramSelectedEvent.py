class PresetProgramSelectedEvent(object):
    def __init__(self, preset_index):
        # type: (int) -> None
        self.preset_index = preset_index
