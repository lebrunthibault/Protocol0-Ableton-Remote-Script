from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack


def assert_valid_track_name(track_name):
    # type: (str) -> None
    from protocol0.domain.lom.device.DeviceEnum import DeviceEnum

    excluded_names = [d.value.lower() for d in DeviceEnum if d.is_instrument]
    excluded_names += ["synth"]

    assert track_name.lower() not in excluded_names, "Track name should be specific"

def assert_no_duplicate_midi_clip(track):
    # type: (SimpleMidiTrack) -> None
    duplicates = len(set([c.midi_hash for c in track.clips])) != len(track.clips)
    assert not duplicates, "Duplicate midi clips in track to flatten"