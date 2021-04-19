from a_protocol_0.devices.InstrumentProphet import InstrumentProphet
from a_protocol_0.lom.Song import Song
from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from a_protocol_0.tests.fixtures.simple_track import make_midi_track, make_audio_track, make_group_track


def make_external_synth_track(song, name=InstrumentProphet.NAME):
    # type: (Song, str) -> ExternalSynthTrack
    track_group = make_group_track(song, name)
    make_midi_track(song)
    make_audio_track(song)
    # noinspection PyTypeChecker
    return ExternalSynthTrack(song, track_group)
