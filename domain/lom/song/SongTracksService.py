import collections

from typing import Optional, Dict

from _Framework.SubjectSlot import subject_slot
from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.song.Song import Song
from protocol0.domain.lom.song.TrackAddedEvent import TrackAddedEvent
from protocol0.domain.lom.song.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.track.simple_track.SimpleMasterTrack import SimpleMasterTrack
from protocol0.domain.lom.track.simple_track.SimpleReturnTrack import SimpleReturnTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackCreatedEvent import SimpleTrackCreatedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class SongTracksService(UseFrameworkEvents):
    def __init__(self, track_factory, song):
        # type: (TrackFactory, Song) -> None
        super(SongTracksService, self).__init__()
        self._track_factory = track_factory
        self._song = song

        self._live_track_id_to_simple_track = collections.OrderedDict()  # type: Dict[int, SimpleTrack]
        self._template_dummy_clip = None  # type: Optional[AudioClip]
        self._usamo_track = None  # type: Optional[SimpleTrack]
        self._master_track = None  # type: Optional[SimpleTrack]

        self.tracks_listener.subject = self._song._song
        DomainEventBus.subscribe(SimpleTrackCreatedEvent, self._on_simple_track_created_event)

    @subject_slot("tracks")
    def tracks_listener(self):
        # type: () -> None
        self._clean_deleted_tracks()

        previous_simple_track_count = len(list(SongFacade.all_simple_tracks()))
        has_added_tracks = 0 < previous_simple_track_count < len(list(SongFacade.live_tracks()))

        self._generate_simple_tracks()
        self._generate_abstract_group_tracks()

        for scene in SongFacade.scenes():
            scene.on_tracks_change()

        Logger.log_info("mapped tracks")

        if has_added_tracks and SongFacade.selected_track():
            DomainEventBus.notify(TrackAddedEvent())

        DomainEventBus.notify(TracksMappedEvent())

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
        self._usamo_track = None
        self.template_dummy_clip = None  # type: Optional[AudioClip]

        # instantiate set tracks
        for index, track in enumerate(list(self._song._song.tracks)):
            self._track_factory.create_simple_track(track=track, index=index)

        if self._usamo_track is None:
            Logger.log_warning("Usamo track is not present")

        for index, track in enumerate(list(self._song._song.return_tracks)):
            self._track_factory.create_simple_track(track=track, index=index, cls=SimpleReturnTrack)

        self._master_track = self._track_factory.create_simple_track(track=self._song._song.master_track, index=0,
                                                                     cls=SimpleMasterTrack)

        self._sort_simple_tracks()

    def _on_simple_track_created_event(self, event):
        # type: (SimpleTrackCreatedEvent) -> None
        """ So as to be able to generate simple tracks with the abstract group track aggregate """
        event.track.set_song(self._song)
        self._register_simple_track(event.track)
        event.track.on_tracks_change()

        if self._usamo_track is None:
            if event.track.get_device_from_enum(DeviceEnum.USAMO):
                self._usamo_track = event.track

        if event.track.name == SimpleInstrumentBusTrack.DEFAULT_NAME and len(event.track.clips):
            self._template_dummy_clip = event.track.clips[0]

    def _register_simple_track(self, simple_track):
        # type: (SimpleTrack) -> None
        # rebuild sub_tracks
        simple_track.sub_tracks = []

        # handling replacement of a SimpleTrack by another
        previous_simple_track = SongFacade.optional_simple_track_from_live_track(simple_track._track)
        if previous_simple_track and previous_simple_track != simple_track:
            self._replace_simple_track(previous_simple_track, simple_track)

        self._live_track_id_to_simple_track[simple_track.live_id] = simple_track

    def _replace_simple_track(self, previous_simple_track, new_simple_track):
        # type: (SimpleTrack, SimpleTrack) -> None
        """ disconnecting and removing from SimpleTrack group track and abstract_group_track """
        new_simple_track._index = previous_simple_track._index
        previous_simple_track.disconnect()

        if previous_simple_track.group_track:
            previous_simple_track.append_to_sub_tracks(previous_simple_track.group_track, new_simple_track,
                                                       previous_simple_track)

        if previous_simple_track.abstract_group_track:
            previous_simple_track.append_to_sub_tracks(previous_simple_track.abstract_group_track, new_simple_track,
                                                       previous_simple_track)

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
            abstract_group_track.set_song(self._song)

            if isinstance(previous_abstract_group_track, ExternalSynthTrack) and isinstance(abstract_group_track,
                                                                                            NormalGroupTrack):
                Logger.log_error("An ExternalSynthTrack is changed to a NormalGroupTrack")

            if previous_abstract_group_track and previous_abstract_group_track != abstract_group_track:
                previous_abstract_group_track.disconnect()

            abstract_group_track.on_tracks_change()
