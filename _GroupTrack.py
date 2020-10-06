from ClyphX_Pro.clyphx_pro.user_actions._Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions._Track import Track
from ClyphX_Pro.clyphx_pro.user_actions._TrackType import TrackType


class GroupTrack:
    def __init__(self, song, base_track):
        self.song = song
        self.track_index_clyphx = list(self.song.tracks).index(base_track) + 1

        # check if we clicked on group track instead of clyphx track
        if list(song.tracks)[self.track_index_clyphx - 1].is_foldable:
            self.track_index_clyphx += 1

        if self.track_index_clyphx < 2:
            raise Exception(
                "tried to instantiate group track with base_track {0} and found track index {1}".format(base_track,
                                                                                                        self.track_index_clyphx))

    @staticmethod
    def is_groupable(track):
        return track and (track.name == GroupTrack.GROUP_CLYPHX_NAME or track.name in GroupTrack.GROUP_EXT_NAMES)

    @property
    def is_group_track(self):
        # type: () -> bool
        return self.clyphx.track.name == GroupTrack.GROUP_CLYPHX_NAME

    @property
    def selectable_track(self):
        # type: () -> Track
        return self.midi if self.name == "Prophet Group" else self.audio

    @property
    def index(self):
        # type: () -> int
        return self.group.index

    @property
    def group(self):
        # type: () -> Track
        track_index = self.track_index_clyphx - 1
        track = list(self.song.tracks)[track_index - 1]
        return Track(track, track_index, self, TrackType.group)

    @property
    def clyphx(self):
        # type: () -> Track
        track_index = self.track_index_clyphx
        track = list(self.song.tracks)[track_index - 1]
        return Track(track, track_index, self, TrackType.clyphx)

    @property
    def midi(self):
        # type: () -> Track
        track_index = self.track_index_clyphx + 1
        track = list(self.song.tracks)[track_index - 1]
        return Track(track, track_index, self, TrackType.midi)

    @property
    def audio(self):
        # type: () -> Track
        track_index = self.track_index_clyphx + 2
        track = list(self.song.tracks)[track_index - 1]
        return Track(track, track_index, self, TrackType.audio)

    @property
    def name(self):
        # type: () -> str
        return self.group.name

    @property
    def is_armed(self):
        # type: () -> bool
        return self.midi.arm and self.audio.arm

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi.is_playing or self.audio.is_playing

    @property
    def color(self):
        if "Prophet" in self.group.name:
            return Colors.PROPHET
        elif "BS" in self.group.name:
            return Colors.BASS_STATION
        return Colors.DISABLED

    @property
    def other_group_tracks(self):
        # type: (GroupTrack) -> list[GroupTrack]
        return [GroupTrack(self.song, track) for track in self.song.tracks if
                track.name in self.GROUP_EXT_NAMES and track != self.group.track]

    @property
    def other_armed_group_track(self):
        # type: (GroupTrack) -> GroupTrack
        return next(iter([g_track for g_track in self.other_group_tracks if g_track.is_armed]), None)
