from protocol0.application.command.SerializableCommand import SerializableCommand


class LoadDrumRackCommand(SerializableCommand):
    def __init__(self, sample_category, sample_subcategory):
        # type: (str, str) -> None
        super(LoadDrumRackCommand, self).__init__()
        self.sample_category = sample_category
        self.sample_subcategory = sample_subcategory
