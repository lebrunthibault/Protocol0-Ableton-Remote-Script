from _Framework.SubjectSlot import Subject


class AbletonDevice(Subject):
    __subject_events__ = (
        "parameters",
    )

    def __init__(self, name):
        # type: (str) -> None
        self.name = name
        self.view = None
        self.parameters = []
        self.can_have_drum_pads = False
        self.can_have_chains = False
