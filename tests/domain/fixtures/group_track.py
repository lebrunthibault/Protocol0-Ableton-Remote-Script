from protocol0.domain.lom.device.Device import Device
from protocol0.tests.domain.fixtures.device import AbletonDevice
from protocol0.tests.domain.fixtures.simple_track import add_track, AbletonTrack, TrackType


def add_external_synth_track(add_tail=False):
    # type: (bool) -> AbletonTrack
    group_track = add_track(track_type=TrackType.GROUP)
    midi_track = add_track(track_type=TrackType.MIDI)
    # add external device
    midi_track.devices.append(AbletonDevice("Ext. Audio Effect"))
    audio_track = add_track(track_type=TrackType.AUDIO)
    midi_track.group_track = group_track
    audio_track.group_track = group_track

    Device._get_class = classmethod(lambda _, __: Device)

    if add_tail:
        audio_tail_track = add_track(track_type=TrackType.AUDIO)
        audio_tail_track.group_track = group_track
    return group_track
