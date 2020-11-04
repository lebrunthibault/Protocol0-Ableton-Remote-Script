from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName
from ClyphX_Pro.clyphx_pro.user_actions.tests.fixtures.simpleTrack import \
    make_clyphx_track, make_midi_track, make_audio_track, make_group_track


def make_group_ex_track(song, name=TrackName.GROUP_PROPHET_NAME):
    # type: (Song, str) -> GroupTrack
    track_group = make_group_track(song, name)
    make_clyphx_track(song)
    make_midi_track(song)
    make_audio_track(song)
    return GroupTrack(song, track_group.track)
