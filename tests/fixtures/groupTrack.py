from a_protocol_0.consts import GROUP_PROPHET_NAME
from a_protocol_0.lom.Song import Song
from a_protocol_0.lom.track.GroupTrack import GroupTrack
from a_protocol_0.tests.fixtures.simpleTrack import \
    make_midi_track, make_audio_track, make_group_track


def make_group_ex_track(song, name=GROUP_PROPHET_NAME):
    # type: (Song, str) -> GroupTrack
    track_group = make_group_track(song, name)
    make_midi_track(song)
    make_audio_track(song)
    return GroupTrack(song, track_group)
