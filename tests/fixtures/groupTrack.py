from a_protocol_0.consts import EXTERNAL_SYNTH_PROPHET_NAME
from a_protocol_0.lom.Song import Song
from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.tests.fixtures.simpleTrack import \
    make_midi_track, make_audio_track, make_group_track


def make_external_synth_track(song, name=EXTERNAL_SYNTH_PROPHET_NAME):
    # type: (Song, str) -> ExternalSynthTrack
    track_group = make_group_track(song, name)
    make_midi_track(song)
    make_audio_track(song)
    # noinspection PyTypeChecker
    return ExternalSynthTrack(song, track_group)
