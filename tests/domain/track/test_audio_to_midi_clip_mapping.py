from protocol0 import EmptyModule
from protocol0.domain.lom.track.simple_track.AudioToMidiClipMapping import AudioToMidiClipMapping

class ClipInfoTest(object):
    def __init__(self, clip_hash):
        self.hash = clip_hash


# noinspection PyTypeChecker
def test_audio_to_midi_clip_mapping():
    mapping = AudioToMidiClipMapping(EmptyModule())  # noqa
    mapping.register_file_path("path1", ClipInfoTest(1))
    mapping.register_file_path("path1_bis", ClipInfoTest(1))
    mapping.register_file_path("path2", ClipInfoTest(2))
    # modify the midi clip
    mapping.register_hash_equivalence(1, 11)

    assert mapping.path_matches_hash("path1", 1, False)
    assert not mapping.path_matches_hash("path1", 2, False)
    assert mapping.path_matches_hash("path1", 11, False)
