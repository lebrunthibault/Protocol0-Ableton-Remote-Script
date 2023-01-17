from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.ReloadScriptCommand import ReloadScriptCommand
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.domain.lom.track.simple_track.audio.dummy.SimpleDummyTrack import SimpleDummyTrack
from protocol0.shared.Song import Song
from protocol0.tests.domain.fixtures.group_track import add_external_synth_track
from protocol0.tests.domain.fixtures.p0 import make_protocol0
from protocol0.tests.domain.fixtures.simple_track import TrackType, add_track


def test_instantiation_simple():
    make_protocol0()
    add_track(track_type=TrackType.MIDI)
    add_track(track_type=TrackType.AUDIO)
    CommandBus.dispatch(ReloadScriptCommand())
    assert len(list(Song.simple_tracks())) == 3


def test_instantiation_external_synth_track():
    make_protocol0()
    add_external_synth_track()
    CommandBus.dispatch(ReloadScriptCommand())
    assert len(list(Song.simple_tracks())) == 4
    assert len(list(Song.external_synth_tracks())) == 1


def test_instantiation_external_synth_track_with_tail():
    make_protocol0()
    group_track = add_external_synth_track(add_tail=True)
    CommandBus.dispatch(ReloadScriptCommand())
    assert len(list(Song.simple_tracks())) == 5
    assert len(list(Song.external_synth_tracks())) == 1
    assert isinstance(list(Song.simple_tracks())[-1], SimpleAudioTailTrack)

    # add dummy track
    track = add_track(track_type=TrackType.AUDIO)
    track.group_track = group_track
    CommandBus.dispatch(ReloadScriptCommand())
    assert len(list(Song.simple_tracks())) == 6
    assert len(list(Song.external_synth_tracks())) == 1
    assert isinstance(list(Song.simple_tracks())[-1], SimpleDummyTrack)
