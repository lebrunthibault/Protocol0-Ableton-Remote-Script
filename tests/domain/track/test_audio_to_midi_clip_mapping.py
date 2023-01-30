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

    assert not mapping.hash_matches_file_path(1, "path1")
    assert mapping.hash_matches_file_path(1, "path1", exclude_identity=False)
    assert not mapping.hash_matches_file_path(2, "path1")
    assert mapping.hash_matches_file_path(11, "path1")

    assert not mapping.file_path_updated_matches_file_path("path1", "path1_bis")
    assert mapping.file_path_updated_matches_file_path("path1", "path1_bis", exclude_identity=False)
    assert not mapping.file_path_updated_matches_file_path("path1", "path2")

    mapping.register_file_path("path3", ClipInfoTest(3))
    assert not mapping.file_path_updated_matches_file_path("path1", "path3")
    mapping.register_midi_hash_equivalence(1, 3)
    assert mapping.file_path_updated_matches_file_path("path1", "path3")
    assert mapping.file_path_updated_matches_file_path("path1_bis", "path3")
