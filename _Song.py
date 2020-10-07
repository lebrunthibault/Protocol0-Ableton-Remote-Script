from ClyphX_Pro.clyphx_pro.user_actions._GroupTrack import GroupTrack
from ClyphX_Pro.clyphx_pro.user_actions._Track import Track
from ClyphX_Pro.clyphx_pro.user_actions._TrackName import TrackName


class MySong:
    def __init__(self, song):
        # type: (_) -> None
        self.song = song
        self.tracks = [Track(track, i + 1) for i, track in enumerate(list(song.tracks))]

    @property
    def tempo(self):
        return self.song.tempo

    @property
    def view(self):
        return self.song.view

    @property
    def visible_tracks(self):
        return [track for track in self.tracks if track.is_visible]

    @property
    def armed_tracks(self):
        return [track for track in self.tracks if track.can_be_armed and track.arm]

    @property
    def group_ex_tracks(self):
        # type: () -> list[GroupTrack]
        return [GroupTrack(self, track) for track in self.tracks if
                track.name in TrackName.GROUP_EXT_NAMES]

    @property
    def selected_track(self):
        # type: () -> Track
        if self.view.selected_track:
            return Track(self.view.selected_track, self.song.tracks.index(self.view.selected_track + 1))
        else:
            return None

    def playing_clips_count(self, g_track, include_group):
        # type: (GroupTrack, bool) -> int
        """ number of playing clip count in the live set excluding the group track """
        playing_clips_count = len([clip_slot for track in self.tracks for clip_slot in track.clip_slots
                                   if (include_group is True or track.index not in (
                                       g_track.midi.index, g_track.audio.index))
                                   and clip_slot.clip
                                   and not clip_slot.clip.name.startswith("[]")
                                   and clip_slot.clip.is_playing])

        return playing_clips_count

    def has_set_playing_clips(self, g_track, include_group=True):
        # type: (GroupTrack, bool) -> bool
        """ find if there is playing clips elsewhere
            by default checks also in group track
        """
        return self.playing_clips_count(g_track, include_group) != 0

    def get_track(self, track):
        # type: (_) -> Track
        for t in self.tracks:
            if t.track == track:
                return t

        raise Exception("this track cannot be matched")
