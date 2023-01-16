class RecordStartedEvent(object):
    def __init__(self, scene_index, full_record, has_count_in):
        # type: (int, bool, bool) -> None
        self.scene_index = scene_index
        self.full_record = full_record
        self.has_count_in = has_count_in
