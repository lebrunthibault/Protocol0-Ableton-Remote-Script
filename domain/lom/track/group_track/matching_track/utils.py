def assert_valid_track_name(track_name):
    # type: (str) -> None
    from protocol0.domain.lom.device.DeviceEnum import DeviceEnum

    excluded_names = [d.value.lower() for d in DeviceEnum if d.is_instrument]
    excluded_names += ["synth"]

    assert track_name.lower() not in excluded_names, "Track name should be specific"
