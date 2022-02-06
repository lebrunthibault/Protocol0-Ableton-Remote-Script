from protocol0.domain.lom.track.simple_track.SimpleAudioTailTrack import SimpleAudioTailTrack
from protocol0.tests.fixtures import patch_song
from protocol0.tests.fixtures.simple_track import TrackType, add_external_synth_track, add_track


def test_instantiation_simple():
    # return
    song = patch_song()
    add_track(track_type=TrackType.MIDI)
    add_track(track_type=TrackType.AUDIO)
    from protocol0 import Protocol0
    Protocol0.SELF.songTracksManager.tracks_listener()
    assert len(list(song.simple_tracks)) == 2


def test_instantiation_external_synth_track():
    # return
    song = patch_song()
    add_external_synth_track()
    from protocol0 import Protocol0
    Protocol0.SELF.songTracksManager.tracks_listener()
    assert len(list(song.simple_tracks)) == 3
    assert len(list(song.external_synth_tracks)) == 1


def test_instantiation_external_synth_track_with_tail():
    # return
    song = patch_song()
    add_external_synth_track(add_tail=True)
    from protocol0 import Protocol0
    Protocol0.SELF.songTracksManager.tracks_listener()
    assert len(list(song.simple_tracks)) == 4
    assert len(list(song.external_synth_tracks)) == 1
    assert isinstance(list(song.simple_tracks)[-1], SimpleAudioTailTrack)

    # should implement routings in fixtures to have no error
    # track = add_track(song, track_type=TrackType.AUDIO)
    # track.group_track = group_track
    # song.parent.songTracksManager.tracks_listener()
    # assert len(list(song.simple_tracks)) == 5
    # assert len(list(song.external_synth_tracks)) == 1
    # assert isinstance(list(song.simple_tracks)[-1], SimpleDummyTrack)
