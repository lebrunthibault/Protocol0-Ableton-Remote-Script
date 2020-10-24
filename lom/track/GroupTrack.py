from typing import Any, TYPE_CHECKING

from ClyphX_Pro.clyphx_pro.user_actions.actions.mixins.GroupTrackActionMixin import GroupTrackActionMixin
from ClyphX_Pro.clyphx_pro.user_actions.instruments.AbstractInstrument import AbstractInstrument
from ClyphX_Pro.clyphx_pro.user_actions.lom.Colors import Colors
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
from ClyphX_Pro.clyphx_pro.user_actions.lom.track.TrackName import TrackName

if TYPE_CHECKING:
    from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song

class GroupTrack(GroupTrackActionMixin, AbstractTrack):
    def __init__(self, song, base_track):
        # type: ("Song", Any) -> None
        # getting our track object
        track = song.get_track(base_track)
        self.song = song # type: Song
        self.track_index_group = track.index - 1 # type: int

        # check if we clicked on group track instead of clyphx track
        if track.is_clyphx:
            self.track_index_group -= 1

        if track.index >= 3 and song.tracks[track.index - 2].name == TrackName.GROUP_CLYPHX_NAME:
            self.track_index_group -= 2
        if track.index >= 4 and song.tracks[track.index - 3].name == TrackName.GROUP_CLYPHX_NAME:
            self.track_index_group -= 3

        if self.track_index_group < 0 or self.track_index_group > len(song.tracks) - 2:
            raise Exception(
                "tried to instantiate group track with base_track {0} and found track index {1}".format(base_track,
                                                                                                        self.track_index_group))
        super(GroupTrack, self).__init__(song, self.group.track, self.track_index_group)

        self.clyphx.g_track = self.midi.g_track = self.audio.g_track = self

    @property
    def track(self):
        # type: () -> int
        return self.group.track

    def instrument(self):
        # type: () -> AbstractInstrument
        return self.selectable_track.instrument

    @property
    def index(self):
        # type: () -> int
        return self.group.index

    @property
    def scene_count(self):
        return self.audio.scene_count

    @property
    def first_empty_slot_index(self):
        return self.audio.first_empty_slot_index

    @property
    def name(self):
        # type: () -> str
        return self.group.name

    @property
    def is_foldable(self):
        # type: () -> bool
        return True

    @property
    def is_folded(self):
        # type: () -> bool
        return self.group.track.is_folded

    @property
    def is_prophet_group_track(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_PROPHET_NAME

    @property
    def is_minitaur_group_track(self):
        # type: () -> bool
        return self.name == TrackName.GROUP_MINITAUR_NAME

    @property
    def selectable_track(self):
        # type: () -> SimpleTrack
        return self.midi if self.is_prophet_group_track else self.audio

    @property
    def is_visible(self):
        # type: () -> bool
        return True

    @property
    def is_top_visible(self):
        # type: () -> bool
        return True

    @property
    def has_empty_slot(self):
        # type: () -> int
        return self.audio.has_empty_slot

    @property
    def group(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group]

    @property
    def clyphx(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 1]

    @property
    def midi(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 2]

    @property
    def audio(self):
        # type: () -> SimpleTrack
        return self.song.tracks[self.track_index_group + 3]

    @property
    def is_armed(self):
        # type: () -> bool
        return self.midi.is_armed and self.audio.is_armed

    @property
    def any_armed(self):
        # type: () -> bool
        return self.clyphx.is_armed or self.midi.is_armed or self.audio.is_armed

    @property
    def can_be_armed(self):
        # type: () -> bool
        return True

    @property
    def is_playing(self):
        # type: () -> bool
        return self.midi.is_playing or self.audio.is_playing

    @property
    def is_recording(self):
        # type: () -> bool
        return self.midi.is_recording or self.audio.is_recording

    @property
    def color(self):
        # type: () -> str
        if "Prophet" in self.group.name:
            return Colors.PROPHET
        elif "BS" in self.group.name:
            return Colors.BASS_STATION
        return Colors.DISABLED

    @property
    def rec_clip_index(self):
        # type: () -> int
        return self.audio.rec_clip_index

    @property
    def record_track(self):
        # type: () -> SimpleTrack
        return self.audio

    @property
    def rec_length_from_midi(self):
        # type: () -> int
        return int(round((self.midi.playing_clip.length + 1) / 4))

    @property
    def delay_before_recording_end(self):
        # type: () -> int
        return int(round((600 / self.song.tempo) * (int(self.midi.playing_clip.length) + 6)))
