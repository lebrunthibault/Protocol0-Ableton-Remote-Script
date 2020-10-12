from ClyphX_Pro.clyphx_pro.user_actions._Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions._Track import Track
from ClyphX_Pro.clyphx_pro.user_actions._TrackName import TrackName


class GroupTrack:
    def __init__(self, song, base_track):
        # type: ("Song", _) -> None
        self.song = song
        # getting our track object
        track = self.song.get_track(base_track)
        self.track_index_group = track.index - 1

        # check if we clicked on group track instead of clyphx track
        if track.is_clyphx:
            self.track_index_group -= 1

        if track.index >= 3 and self.song.tracks[track.index - 2].name == TrackName.GROUP_CLYPHX_NAME:
            self.track_index_group -= 2
        if track.index >= 4 and self.song.tracks[track.index - 3].name == TrackName.GROUP_CLYPHX_NAME:
            self.track_index_group -= 3

        if self.track_index_group < 0 or self.track_index_group > len(self.song.tracks) - 2:
            raise Exception(
                "tried to instantiate group track with base_track {0} and found track index {1}".format(base_track,
                                                                                                        self.track_index_group))
        self.clyphx.g_track = self.midi.g_track = self.audio.g_track = self

    @property
    def is_group_track(self):
        # type: () -> bool
        return self.clyphx.track.name == TrackName.GROUP_CLYPHX_NAME

    @property
    def is_prophet(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_PROPHET_NAME

    @property
    def is_minitaur(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_MINITAUR_NAME

    @property
    def selectable_track(self):
        # type: () -> Track
        return self.midi if self.is_prophet else self.audio

    @property
    def index(self):
        # type: () -> int
        return self.group.index

    @property
    def group(self):
        # type: () -> Track
        return self.song.tracks[self.track_index_group]

    @property
    def clyphx(self):
        # type: () -> Track
        return self.song.tracks[self.track_index_group + 1]

    @property
    def midi(self):
        # type: () -> Track
        return self.song.tracks[self.track_index_group + 2]

    @property
    def audio(self):
        # type: () -> Track
        return self.song.tracks[self.track_index_group + 3]

    @property
    def name(self):
        # type: () -> str
        return self.group.name

    @property
    def is_armed(self):
        # type: () -> bool
        return self.midi.arm and self.audio.arm

    @property
    def any_armed(self):
        # type: () -> bool
        return self.clyphx.arm or self.midi.arm or self.audio.arm

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi.is_playing or self.audio.is_playing

    @property
    def color(self):
        # type: () -> str
        if "Prophet" in self.group.name:
            return Colors.PROPHET
        elif "BS" in self.group.name:
            return Colors.BASS_STATION
        return Colors.DISABLED

    @property
    def other_group_tracks(self):
        # type: (GroupTrack) -> list[GroupTrack]
        return [g_track for g_track in self.song.group_ex_tracks if g_track.index != self.index]

    @property
    def other_armed_group_track(self):
        # type: (GroupTrack) -> GroupTrack
        return next(iter([g_track for g_track in self.other_group_tracks if g_track.any_armed]), None)

    @property
    def beat_count_before_clip_restart(self):
        # type: () -> int
        if self.audio.beat_count_before_clip_restart:
            return self.audio.beat_count_before_clip_restart
        else:
            return self.midi.beat_count_before_clip_restart
