from ClyphX_Pro.clyphx_pro.user_actions._Track import Track
from ClyphX_Pro.clyphx_pro.user_actions._TrackType import TrackType


class GroupTrack:
    GROUP_EXT_NAMES = ("Prophet Group", "BS Group")

    def __init__(self, song, base_track):
        self.song = song
        self.track_index_clyphx = list(self.song.tracks).index(base_track) + 1

        # check if we clicked on group track instead of clyphx track
        if list(song.tracks)[self.track_index_clyphx - 1].is_foldable:
            self.track_index_clyphx += 1

    @property
    def group(self):
        # type: () -> Track
        track_index = self.track_index_clyphx - 1
        track = list(self.song.tracks)[track_index - 1]
        return Track(self, track, track_index, TrackType.group)

    @property
    def clyphx(self):
        # type: () -> Track
        track_index = self.track_index_clyphx
        track = list(self.song.tracks)[track_index - 1]
        return Track(self, track, track_index, TrackType.clyphx)

    @property
    def midi(self):
        # type: () -> Track
        track_index = self.track_index_clyphx + 1
        track = list(self.song.tracks)[track_index - 1]
        return Track(self, track, track_index, TrackType.midi)

    @property
    def audio(self):
        # type: () -> Track
        track_index = self.track_index_clyphx + 2
        track = list(self.song.tracks)[track_index - 1]
        return Track(self, track, track_index, TrackType.audio)

    @property
    def is_armed(self):
        # type: () -> bool
        return self.midi.arm and self.audio.arm

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi.is_playing or self.audio.is_playing

    @property
    def other_group_tracks(self):
        # type: (GroupTrack) -> list[GroupTrack]
        return [GroupTrack(self.song, track) for track in self.song.tracks if
                              track.name in self.GROUP_EXT_NAMES and track != self.group.track]

    @property
    def other_armed_group_track(self):
        # type: (GroupTrack) -> GroupTrack
        return next(iter([g_track for g_track in self.other_group_tracks if g_track.is_armed]), None)
