from protocol0 import EmptyModule
from protocol0.domain.lom.track.simple_track.AudioToMidiClipMapping import AudioToMidiClipMapping

class ClipInfoTest(object):
    def __init__(self, midi_hash):
        self.midi_hash = midi_hash


# noinspection PyTypeChecker
def test_audio_to_midi_clip_mapping():
    mapping = AudioToMidiClipMapping(EmptyModule())  # noqa
    mapping.register_file_path("path1", ClipInfoTest(1))
    mapping.register_file_path("path1_bis", ClipInfoTest(1))
    mapping.register_file_path("path2", ClipInfoTest(2))
    # modify the midi clip
    mapping.register_midi_hash_equivalence(1, 11)

    assert mapping.hash_matches_path(1, "path1", False)
    assert not mapping.hash_matches_path(2, "path1", False)
    assert mapping.hash_matches_path(11, "path1", False)

    assert mapping.path_matches_path("path1", "path1_bis", False)
    assert not mapping.path_matches_path("path1", "path2", False)

    mapping.register_file_path("path3", ClipInfoTest(3))
    assert not mapping.path_matches_path("path1", "path3", False)
    mapping.register_midi_hash_equivalence(1, 3)
    assert mapping.path_matches_path("path1", "path3", False)
    assert mapping.path_matches_path("path1_bis", "path3", False)
