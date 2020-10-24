from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
    from ClyphX_Pro.clyphx_pro.user_actions.lom.track.AbstractTrack import AbstractTrack


class TrackName:
    GROUP_PROPHET_NAME = "Prophet"
    GROUP_MINITAUR_NAME = "Minitaur"
    GROUP_EXT_NAMES = (GROUP_PROPHET_NAME, GROUP_MINITAUR_NAME)
    GROUP_CLYPHX_NAME = "Clyphx"

    def __init__(self, abstract_track):
        # type: (AbstractTrack) -> None
        self.parts = abstract_track.track.name.split(" - ")
        self.track = abstract_track
        self.name = self.parts[0]
        try:
            self.clip_index = int(self.parts[1])
        except (ValueError, IndexError):
            self.clip_index = 0
        try:
            self.preset_index = int(self.parts[2])
        except (ValueError, IndexError):
            self.preset_index = -1

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, TrackName):
            return self.name == other.name
        elif isinstance(other, str):
            return self.name == str
        return False

    @property
    def is_group_track(self):
        return self.name in TrackName.GROUP_EXT_NAMES

    @property
    def is_prophet_group_track(self):
        return self.name == TrackName.GROUP_PROPHET_NAME

    @property
    def is_minitaur_group_track(self):
        return self.name == TrackName.GROUP_MINITAUR_NAME

    @property
    def is_clyphx(self):
        return self.name == TrackName.GROUP_CLYPHX_NAME

    @property
    def has_instrument_preset(self):
        return len(self.parts) >= 3

    def get_track_name_for_playing_clip_index(self, playing_clip_index=None):
        # type: (Optional[int]) -> str
        from ClyphX_Pro.clyphx_pro.user_actions.lom.track.SimpleTrack import SimpleTrack
        if not isinstance(self.track, SimpleTrack):
            return self.name

        name = "{0} - {1}".format(self.name,
                                  playing_clip_index if playing_clip_index is not None else self.track.playing_clip.index)

        if self.has_instrument_preset:
            name += " - {0}".format(self.preset_index)

        return name

    def get_track_name_for_preset_index(self, preset_index):
        # type: (int) -> str
        return "{0} - {1} - {2}".format(self.name, self.clip_index, preset_index)




