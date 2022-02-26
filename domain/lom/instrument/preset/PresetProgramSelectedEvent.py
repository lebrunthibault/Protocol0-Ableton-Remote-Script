class PresetProgramSelectedEvent(object):
    def __init__(self, preset_index):
        # type: (int) -> None
        assert 0 <= preset_index <= 127
        self.preset_index = preset_index
