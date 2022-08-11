from functools import partial

from _Framework.SubjectSlot import SlotManager
from typing import Optional, List, Iterator, cast, TYPE_CHECKING, Dict

import Live
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipSlotSelectedEvent import ClipSlotSelectedEvent
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.abstract_track.AbstrackTrackArmState import AbstractTrackArmState
from protocol0.domain.lom.track.abstract_track.AbstractTrackAppearance import (
    AbstractTrackAppearance,
)
from protocol0.domain.lom.track.abstract_track.AbstractTrackSelectedEvent import (
    AbstractTrackSelectedEvent,
)
from protocol0.domain.lom.track.routing.TrackInputRouting import TrackInputRouting
from protocol0.domain.lom.track.routing.TrackOutputRouting import TrackOutputRouting
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.domain.shared.utils.utils import volume_to_db, db_to_volume
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack


class AbstractTrack(SlotManager):
    # when the color cannot be matched
    REMOVE_CLIPS_ON_ADDED = False

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

        # MISC
        self.arm_state = AbstractTrackArmState(self._track)  # type: AbstractTrackArmState
        self.appearance = AbstractTrackAppearance(self._track)  # type: AbstractTrackAppearance
        self.input_routing = TrackInputRouting(self.base_track._track)
        self.output_routing = TrackOutputRouting(self.base_track._track)

        self.protected_mode_active = True

    def __repr__(self):
        # type: () -> str
        return "%s : %s (%s)" % (self.__class__.__name__, self.name, self.index + 1)

    def __iter__(self):
        # type: () -> Iterator[AbstractTrack]
        return iter(self.sub_tracks)

    def on_added(self):
        # type: () -> Optional[Sequence]
        if self.group_track is not None and self.group_track.color != self.color:
            self.color = self.group_track.color

        if self.REMOVE_CLIPS_ON_ADDED:
            seq = Sequence()
            seq.add([clip.delete for clip in self.clips])
            seq.defer()
            return seq.done()
        else:
            return None

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
        For top level SimpleTracks, will return self
        For AbstractGroupTracks, will return self (NormalGroupTrack and ExternalSynthTrack)
        Only for nested SimpleTracks, will return their abstract_group_track
        """
        if self.abstract_group_track:
            return self.abstract_group_track
        else:
            return self

    @property
    def group_tracks(self):
        # type: () -> List[AbstractGroupTrack]
        if not self.group_track:
            return []
        return [self.group_track.abstract_track] + self.group_track.group_tracks

    @property
    def instrument_track(self):
        # type: () -> SimpleTrack
        assert self.instrument
        return self.base_track

    @property
    def instrument(self):
        # type: () -> Optional[InstrumentInterface]
        return None

    @property
    def clip_slots(self):
        # type: () -> List[ClipSlot]
        raise NotImplementedError

    @property
    def selected_clip_slot(self):
        # type: () -> Optional[ClipSlot]
        return self.clip_slots[SongFacade.selected_scene().index]

    def select_clip_slot(self, clip_slot):
        # type: (Live.ClipSlot.ClipSlot) -> None
        assert clip_slot in [cs._clip_slot for cs in self.clip_slots]
        self.is_folded = False
        DomainEventBus.emit(ClipSlotSelectedEvent(clip_slot))

    @property
    def clips(self):
        # type: () -> List[Clip]
        return [
            clip_slot.clip for clip_slot in self.clip_slots if clip_slot.has_clip and clip_slot.clip
        ]

    name = cast(str, ForwardTo("appearance", "name"))

    @property
    def color(self):
        # type: () -> int
        return self.appearance.color

    @color.setter
    def color(self, color_index):
        # type: (int) -> None
        self.appearance.color = color_index

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
        if not is_folded:
            for group_track in self.group_tracks:
                group_track.is_folded = False
        if self._track and self.is_foldable:
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
    def is_visible(self):
        # type: () -> bool
        return self._track and self._track.is_visible

    @property
    def is_playing(self):
        # type: () -> bool
        return self.base_track.is_playing or any(
            sub_track.is_playing for sub_track in self.sub_tracks
        )

    @property
    def muted(self):
        # type: () -> bool
        return self._track and self._track.mute

    @muted.setter
    def muted(self, mute):
        # type: (bool) -> None
        if self._track:
            self._track.mute = mute

    @property
    def is_recording(self):
        # type: () -> bool
        return False

    @property
    def volume(self):
        # type: () -> float
        volume = self._track.mixer_device.volume.value if self._track else 0
        return volume_to_db(volume)

    @volume.setter
    def volume(self, volume):
        # type: (float) -> None
        volume = db_to_volume(volume)
        if self._track:
            Scheduler.defer(
                partial(
                    DeviceParameter.set_live_device_parameter,
                    self._track.mixer_device.volume,
                    volume,
                )
            )

    @property
    def has_audio_output(self):
        # type: () -> bool
        return self._track and self._track.has_audio_output

    # noinspection PyUnusedLocal
    def select(self):
        # type: () -> Optional[Sequence]
        if SongFacade.selected_track() == self:
            return None

        DomainEventBus.emit(AbstractTrackSelectedEvent(self._track))

        scrollable_tracks = list(SongFacade.scrollable_tracks())
        if len(scrollable_tracks) != 0 and self == scrollable_tracks[-1]:
            ApplicationViewFacade.focus_current_track()
        return Sequence().wait(2).done()

    def stop(self, immediate=False):
        # type: (AbstractTrack, bool) -> None
        # noinspection PyTypeChecker
        self.base_track._track.stop_all_clips(not immediate)

    def scroll_volume(self, go_next):
        # type: (AbstractTrack, bool) -> None
        self.volume += 0.7 if go_next else -0.7

    def get_all_simple_sub_tracks(self):
        # type: () -> List[SimpleTrack]
        sub_tracks = []
        for sub_track in self.sub_tracks:
            if sub_track.is_foldable:
                sub_tracks += sub_track.get_all_simple_sub_tracks()
            else:
                sub_tracks.append(sub_track)

        return sub_tracks  # noqa

    def add_or_replace_sub_track(self, sub_track, previous_sub_track=None):
        # type: (AbstractTrack, AbstractTrack, Optional[AbstractTrack]) -> None
        if sub_track in self.sub_tracks:
            return

        if previous_sub_track is None or previous_sub_track not in self.sub_tracks:
            self.sub_tracks.append(sub_track)
        else:
            sub_track_index = self.sub_tracks.index(previous_sub_track)
            self.sub_tracks[sub_track_index] = sub_track

    def get_automated_parameters(self, index):
        # type: (int) -> Dict[DeviceParameter, SimpleTrack]
        """Due to AbstractGroupTrack we cannot do this only at clip level"""
        raise NotImplementedError

    def scroll_presets(self, go_next):
        # type: (bool) -> Sequence
        assert self.instrument
        seq = Sequence()
        seq.add(self.arm_state.arm)
        seq.add(partial(self.instrument.preset_list.scroll, go_next))
        return seq.done()

    def fire(self, index):
        # type: (int) -> None
        clip = self.clip_slots[index].clip
        if clip:
            clip.fire()

    def disconnect(self):
        # type: () -> None
        super(AbstractTrack, self).disconnect()
        self.appearance.disconnect()
