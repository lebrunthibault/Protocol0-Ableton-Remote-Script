class TrackRecordingStartedEvent(object):
    def __init__(self, recording_scene_index):
        # type: (int) -> None
        self.recording_scene_index = recording_scene_index
