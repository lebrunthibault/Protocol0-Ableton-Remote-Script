from functools import partial

from typing import Optional, List
from typing import TYPE_CHECKING

import Live
from protocol0.domain.enums.ColorEnum import ColorEnum
from protocol0.domain.enums.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.Listenable import Listenable
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.abstract_track.AbstractTrackActionMixin import AbstractTrackActionMixin
from protocol0.domain.lom.track.abstract_track.AbstractTrackName import AbstractTrackName
from protocol0.domain.lom.track.routing.TrackInputRouting import TrackInputRouting
from protocol0.domain.lom.track.routing.TrackOutputRouting import TrackOutputRouting
from protocol0.domain.sequence.Sequence import Sequence
from protocol0.domain.shared.scheduler.Scheduler import Scheduler

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack


class AbstractTrack(AbstractTrackActionMixin, Listenable):
    __subject_events__ = ("devices",)

    DEFAULT_NAME = "default"
    DEFAULT_COLOR = ColorEnum.DISABLED  # when the color cannot be matched
    KEEP_CLIPS_ON_ADDED = False

    def __init__(self, track):
        # type: (SimpleTrack) -> None
        super(AbstractTrack, self).__init__()
        # TRACKS
        self._track = track._track  # type: Live.Track.Track
        self.base_track = track  # type: SimpleTrack
        self.group_track = None  # type: Optional[AbstractTrack]
        # NB : .group_track is simple for simple tracks and abg for abg tracks
        self.abstract_group_track = None  # type: Optional[AbstractGroupTrack]
        self.sub_tracks = []  # type: List[AbstractTrack]

        if not self.base_track.IS_ACTIVE:
            return

        # MISC
        self.track_name = AbstractTrackName(self)  # type: AbstractTrackName
        self.input_routing = TrackInputRouting(self.base_track)
        self.output_routing = TrackOutputRouting(self.base_track)

        self.protected_mode_active = True

    def __repr__(self):
        # type: () -> str
        return "P0 %s : %s (%s)" % (self.__class__.__name__, self.name, self.index + 1)

    def _added_track_init(self):
        # type: () -> Optional[Sequence]
        self.refresh_appearance()
        if self.KEEP_CLIPS_ON_ADDED:
            return None

        seq = Sequence()
        seq.add([clip.delete for clip in self.clips])
        return seq.done()

    def on_tracks_change(self):
        # type: () -> None
        pass

    def on_scenes_change(self):
        # type: () -> None
        pass

    @property
    def index(self):
        # type: () -> int
        return self.base_track._index

    @property
    def abstract_track(self):
        # type: () -> AbstractTrack
        """
        For lone tracks, will return self
        For group_tracks or sub_tracks of AbstractGroupTracks (except NormalGroupTrack)
        will return the AbstractGroupTrack
        """
        return self.abstract_group_track if self.abstract_group_track else self  # type: ignore

    @property
    def active_tracks(self):
        # type: () -> List[AbstractTrack]
        raise NotImplementedError

    @property
    def instrument(self):
        # type: () -> Optional[InstrumentInterface]
        return None

    @property
    def name(self):
        # type: () -> str
        return self._track.name if self._track else ""

    @name.setter
    def name(self, name):
        # type: (str) -> None
        if self._track and name:
            self._track.name = str(name).strip()

    @property
    def computed_base_name(self):
        # type: () -> str
        if self.instrument and self.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.NAME:
            if self.instrument.selected_preset:
                return self.instrument.selected_preset.name
            else:
                return self.instrument.name
        elif self.instrument and self.instrument.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY:
            return self.instrument.preset_list.selected_category
        else:
            return self.DEFAULT_NAME

    @property
    def color(self):
        # type: (AbstractTrack) -> int
        if self._track:
            return self._track.color_index
        else:
            return ColorEnum.DISABLED.index

    @color.setter
    def color(self, color_index):
        # type: (AbstractTrack, int) -> None
        if self._track and color_index != self._track.color_index:
            self._track.color_index = color_index

    @property
    def computed_color(self):
        # type: () -> int
        if self.is_foldable:
            sub_track_colors = [sub_track.color for sub_track in self.sub_tracks]
            if len(set(sub_track_colors)) == 1:
                return sub_track_colors[0]

        instrument = self.instrument or self.abstract_track.instrument
        if instrument:
            return instrument.TRACK_COLOR.index
        else:
            return self.DEFAULT_COLOR.index

    @property
    def is_foldable(self):
        # type: () -> bool
        return self._track and self._track.is_foldable

    @property
    def is_folded(self):
        # type: () -> bool
        return bool(self._track.fold_state) if self.is_foldable and self._track else True

    @is_folded.setter
    def is_folded(self, is_folded):
        # type: (bool) -> None
        if self.is_foldable and self._track:
            self._track.fold_state = int(is_folded)

    @property
    def solo(self):
        # type: () -> bool
        return self._track and self._track.solo

    @solo.setter
    def solo(self, solo):
        # type: (bool) -> None
        if self._track:
            self._track.solo = solo

    @property
    def is_armed(self):
        # type: () -> bool
        return False

    @is_armed.setter
    def is_armed(self, is_armed):
        # type: (bool) -> None
        for track in self.active_tracks:
            track.is_armed = is_armed

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [clip_slot.clip for clip_slot in self.base_track.clip_slots if clip_slot.has_clip and clip_slot.clip]

    @property
    def is_visible(self):
        # type: () -> bool
        return self._track and self._track.is_visible

    @property
    def is_playing(self):
        # type: () -> bool
        return self.base_track.is_playing or any(sub_track.is_playing for sub_track in self.sub_tracks)

    @property
    def mute(self):
        # type: () -> bool
        return self._track and self._track.mute

    @mute.setter
    def mute(self, mute):
        # type: (bool) -> None
        if self._track:
            self._track.mute = mute

    @property
    def is_hearable(self):
        # type: () -> bool
        return (
                self.is_playing
                and self.output_meter_level > 0.2
                and (not self.abstract_group_track or self.abstract_group_track.is_hearable)
        )

    @property
    def is_recording(self):
        # type: () -> bool
        return False

    @property
    def can_be_armed(self):
        # type: () -> bool
        return self._track and self._track.can_be_armed

    @property
    def volume(self):
        # type: () -> float
        return self._track.mixer_device.volume.value if self._track else 0

    @volume.setter
    def volume(self, volume):
        # type: (float) -> None
        if self._track:
            Scheduler.defer(partial(DeviceParameter.set_live_device_parameter, self._track.mixer_device.volume, volume))

    @property
    def has_audio_output(self):
        # type: () -> bool
        return self._track and self._track.has_audio_output

    @property
    def output_meter_level(self):
        # type: () -> float
        return self._track.output_meter_level if self._track else 0

    def disconnect(self):
        # type: () -> None
        super(AbstractTrack, self).disconnect()
        if hasattr(self, "track_name"):
            self.track_name.disconnect()
