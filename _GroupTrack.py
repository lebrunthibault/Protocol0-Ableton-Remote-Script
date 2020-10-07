from ClyphX_Pro.clyphx_pro.user_actions._Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions._Track import Track
from ClyphX_Pro.clyphx_pro.user_actions._TrackName import TrackName
from ClyphX_Pro.clyphx_pro.user_actions._log import log_ableton


class GroupTrack:
    def __init__(self, song, base_track):
        self.song = song
        # getting our track object
        log_ableton("GroupTrack init 1 %s" % base_track.name)
        track = self.song.get_track(base_track)
        log_ableton("GroupTrack init 2 %s" % track.name)
        self.track_index_clyphx = track.index - 1

        # check if we clicked on group track instead of clyphx track
        if track.is_foldable:
            self.track_index_clyphx += 1

        log_ableton("GroupTrack track_index_clyphx %s" % self.track_index_clyphx)

        if self.track_index_clyphx < 1:
            raise Exception(
                "tried to instantiate group track with base_track {0} and found track index {1}".format(base_track,
                                                                                                        self.track_index_clyphx))
        self.clyphx.g_track = self.midi.g_track = self.audio.g_track = self

    @staticmethod
    def is_groupable(track):
        return track and (track.name == TrackName.GROUP_CLYPHX_NAME or track.name in TrackName.GROUP_EXT_NAMES)

    @property
    def is_group_track(self):
        # type: () -> bool
        log_ableton("is_group_track nclypx name %s " % self.clyphx.track.name)
        return self.clyphx.track.name == TrackName.GROUP_CLYPHX_NAME

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
        return self.song.tracks[self.track_index_clyphx - 1]

    @property
    def clyphx(self):
        # type: () -> Track
        return self.song.tracks[self.track_index_clyphx]

    @property
    def midi(self):
        # type: () -> Track
        return self.song.tracks[self.track_index_clyphx + 1]

    @property
    def audio(self):
        # type: () -> Track
        return self.song.tracks[self.track_index_clyphx + 2]

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
        return [g_track for g_track in self.song.group_ex_tracks if g_track.group.track != self.group.track]

    @property
    def other_armed_group_track(self):
        # type: (GroupTrack) -> GroupTrack
        return next(iter([g_track for g_track in self.other_group_tracks if g_track.is_armed]), None)
