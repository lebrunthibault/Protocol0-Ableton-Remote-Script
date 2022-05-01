import collections
from functools import partial

from _Framework.SubjectSlot import subject_slot
from typing import Optional, Dict

from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.song.Song import Song
from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.lom.track.TrackAddedEvent import TrackAddedEvent
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.drums.DrumsTrack import DrumsTrack
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.group_track.external_synth_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.MasterTrack import MasterTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.track.simple_track.SimpleReturnTrack import SimpleReturnTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackCreatedEvent import SimpleTrackCreatedEvent
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.UndoFacade import UndoFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class TrackService(UseFrameworkEvents):
    def __init__(self, track_factory, song):
        # type: (TrackFactory, Song) -> None
        super(TrackService, self).__init__()
        self._track_factory = track_factory
        self._song = song

        self._live_track_id_to_simple_track = collections.OrderedDict()  # type: Dict[int, SimpleTrack]
        self._template_dummy_clip = None  # type: Optional[AudioClip]
        self._usamo_device = None  # type: Optional[Device]
        self._usamo_track = None  # type: Optional[SimpleTrack]
        self._drums_track = None  # type: Optional[DrumsTrack]
        self._master_track = None  # type: Optional[SimpleTrack]

        self.tracks_listener.subject = self._song._song
        self._selected_track_listener.subject = self._song._view  # SongFacade is not hydrated
        DomainEventBus.subscribe(SimpleTrackCreatedEvent, self._on_simple_track_created_event)

    @subject_slot("selected_track")
    def _selected_track_listener(self):
        # type: () -> None
        ApplicationViewFacade.focus_current_track()
        DomainEventBus.emit(SelectedTrackChangedEvent())

    @subject_slot("tracks")
    @handle_error
    def tracks_listener(self):
        # type: () -> None
        self._clean_deleted_tracks()

        previous_simple_track_count = len(list(SongFacade.all_simple_tracks()))
        has_added_tracks = 0 < previous_simple_track_count < len(list(SongFacade.live_tracks()))

        self._generate_simple_tracks()
        self._generate_abstract_group_tracks()

        for scene in SongFacade.scenes():
            scene.on_tracks_change()

        Logger.info("mapped tracks")

        seq = Sequence()
        if has_added_tracks and SongFacade.selected_track():
            seq.add(self._on_track_added_event)
            seq.add(partial(DomainEventBus.defer_emit, TrackAddedEvent()))

        seq.add(partial(DomainEventBus.defer_emit, TracksMappedEvent()))
        seq.done()

    def _clean_deleted_tracks(self):
        # type: () -> None
        existing_track_ids = [track._live_ptr for track in list(SongFacade.live_tracks())]
        deleted_ids = []

        for track_id, simple_track in self._live_track_id_to_simple_track.items():
            if track_id not in existing_track_ids:
                simple_track.disconnect()
                if simple_track.abstract_group_track:
                    simple_track.abstract_group_track.disconnect()
                deleted_ids.append(track_id)

        for track_id in deleted_ids:
            del self._live_track_id_to_simple_track[track_id]

    def _generate_simple_tracks(self):
        # type: () -> None
        """ instantiate SimpleTracks (including return / master, that are marked as inactive) """
        self._usamo_device = None
        self._usamo_track = None
        self._drums_track = None
        self.template_dummy_clip = None  # type: Optional[AudioClip]

        # instantiate set tracks
        for index, track in enumerate(list(self._song._song.tracks)):
            track = self._track_factory.create_simple_track(track=track, index=index)

            usamo_device = track.devices.get_one_from_enum(DeviceEnum.USAMO)
            if usamo_device:
                if self._usamo_device:
                    raise Protocol0Warning("Duplicate usamo track")
                self._usamo_device = usamo_device
                self._usamo_track = track

            if isinstance(track, SimpleInstrumentBusTrack) and len(track.clips):
                self._template_dummy_clip = track.clips[0]

        for index, track in enumerate(list(self._song._song.return_tracks)):
            self._track_factory.create_simple_track(track=track, index=index, cls=SimpleReturnTrack)

        self._master_track = self._track_factory.create_simple_track(track=self._song._song.master_track, index=0,
                                                                     cls=MasterTrack)

        self._sort_simple_tracks()

        for track in SongFacade.simple_tracks():
            track.on_tracks_change()

        if self._usamo_device is None:
            Logger.warning("Usamo track is not present")

    def _on_track_added_event(self):
        # type: () -> Optional[Sequence]
        if not SongFacade.selected_track().IS_ACTIVE:
            return None
        UndoFacade.begin_undo_step()  # Live crashes on undo without this
        seq = Sequence()
        added_track = SongFacade.selected_track()
        if SongFacade.selected_track() == SongFacade.current_track().base_track:
            added_track = SongFacade.current_track()
        seq.defer()
        seq.add(added_track.on_added)
        seq.add(UndoFacade.end_undo_step)
        return seq.done()

    def _on_simple_track_created_event(self, event):
        # type: (SimpleTrackCreatedEvent) -> None
        """ So as to be able to generate simple tracks with the abstract group track aggregate """
        # handling replacement of a SimpleTrack by another
        previous_simple_track = SongFacade.optional_simple_track_from_live_track(event.track._track)
        if previous_simple_track and previous_simple_track != event.track:
            self._replace_simple_track(previous_simple_track, event.track)

        self._live_track_id_to_simple_track[event.track.live_id] = event.track

    def _replace_simple_track(self, previous_simple_track, new_simple_track):
        # type: (SimpleTrack, SimpleTrack) -> None
        """ disconnecting and removing from SimpleTrack group track and abstract_group_track """
        new_simple_track._index = previous_simple_track._index
        previous_simple_track.disconnect()

        if previous_simple_track.group_track:
            previous_simple_track.group_track.add_or_replace_sub_track(new_simple_track, previous_simple_track)

        if previous_simple_track.abstract_group_track:
            previous_simple_track.abstract_group_track.add_or_replace_sub_track(new_simple_track, previous_simple_track)

    def _sort_simple_tracks(self):
        # type: () -> None
        sorted_dict = collections.OrderedDict()
        for track in SongFacade.live_tracks():
            sorted_dict[track._live_ptr] = SongFacade.simple_track_from_live_track(track)
        self._live_track_id_to_simple_track = sorted_dict

    def _generate_abstract_group_tracks(self):
        # type: () -> None
        # 2nd pass : instantiate AbstractGroupTracks
        for track in SongFacade.simple_tracks():
            if not track.is_foldable:
                continue

            previous_abstract_group_track = track.abstract_group_track
            abstract_group_track = self._track_factory.create_abstract_group_track(track)

            if isinstance(previous_abstract_group_track, ExternalSynthTrack) and isinstance(abstract_group_track,
                                                                                            NormalGroupTrack):
                raise Protocol0Error("An ExternalSynthTrack is changed into a NormalGroupTrack")

            if previous_abstract_group_track and previous_abstract_group_track != abstract_group_track:
                previous_abstract_group_track.disconnect()

            abstract_group_track.on_tracks_change()

            if isinstance(abstract_group_track, DrumsTrack):
                self._drums_track = abstract_group_track
