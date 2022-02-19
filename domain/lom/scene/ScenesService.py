import collections
from itertools import chain

from typing import Optional, List, TYPE_CHECKING

import Live
from _Framework.SubjectSlot import subject_slot
from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.ScenesMappedEvent import ScenesMappedEvent
from protocol0.domain.lom.scene.SelectedDuplicateSceneBarLengthUpdatedEvent import \
    SelectedDuplicateSceneBarLengthUpdatedEvent
from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.track.TrackAddedEvent import TrackAddedEvent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import handle_error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.LastBeatPassedEvent import LastBeatPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import scroll_values
from protocol0.domain.track_recorder.TrackRecorderService import TrackRecorderService
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


class ScenesService(UseFrameworkEvents):
    def __init__(self, song, track_recorder_service):
        # type: (Song, TrackRecorderService) -> None
        super(ScenesService, self).__init__()
        self._song = song
        self._track_recorder_service = track_recorder_service
        self.scenes_listener.subject = song._song
        self._live_scene_id_to_scene = collections.OrderedDict()
        self.selected_duplicate_scene_bar_length = 1

        DomainEventBus.subscribe(BarChangedEvent, self._on_bar_changed_event)
        DomainEventBus.subscribe(LastBeatPassedEvent, self._on_last_beat_passed_event)
        DomainEventBus.subscribe(TrackAddedEvent, self._on_track_added_event)
        DomainEventBus.subscribe(SongStartedEvent, self._on_song_started_event)

    def get_scene(self, live_scene):
        # type: (Live.Scene.Scene) -> Scene
        return self._live_scene_id_to_scene[live_scene._live_ptr]

    def get_optional_scene(self, scene):
        # type: (Live.Scene.Scene) -> Optional[Scene]
        try:
            return self.get_scene(scene)
        except KeyError:
            return None

    def add_scene(self, scene):
        # type: (Scene) -> None
        self._live_scene_id_to_scene[scene.live_id] = scene

    @property
    def scenes(self):
        # type: () -> List[Scene]
        return self._live_scene_id_to_scene.values()

    @subject_slot("scenes")
    @handle_error
    def scenes_listener(self):
        # type: () -> None
        self._generate_scenes()
        for scene in SongFacade.scenes():
            Scheduler.defer(scene.refresh_appearance)
        DomainEventBus.defer_notify(ScenesMappedEvent())
        Logger.log_info("mapped scenes")

    def _on_bar_changed_event(self, _):
        # type: (BarChangedEvent) -> None
        if SongFacade.playing_scene():
            SongFacade.playing_scene().scene_name.update()

    def _on_last_beat_passed_event(self, _):
        # type: (LastBeatPassedEvent) -> None
        if SongFacade.playing_scene() and SongFacade.playing_scene().has_playing_clips:
            SongFacade.playing_scene().on_last_beat()

    def _generate_scenes(self):
        # type: () -> None
        self._clean_deleted_scenes()

        # mapping cs should be done before generating the scenes
        for track in collections.OrderedDict.fromkeys(chain(SongFacade.simple_tracks(), SongFacade.abstract_tracks())):
            track.on_scenes_change()

        live_scenes = SongFacade.live_song().scenes
        has_added_scene = 0 < len(SongFacade.scenes()) < len(live_scenes)

        # get the right scene or instantiate new scenes
        for index, live_scene in enumerate(live_scenes):
            self.generate_scene(live_scene, index=index)

        self._sort_scenes()

        if has_added_scene and SongFacade.selected_scene().length and SongFacade.is_playing():
            Scheduler.defer(SongFacade.selected_scene().fire)

    def _clean_deleted_scenes(self):
        # type: () -> None
        existing_scene_ids = [scene._live_ptr for scene in SongFacade.live_song().scenes]
        deleted_ids = []

        for scene_id, scene in self._live_scene_id_to_scene.items():
            if scene_id not in existing_scene_ids:
                scene.disconnect()

        for scene_id in deleted_ids:
            del self._live_scene_id_to_scene[scene_id]

    def generate_scene(self, live_scene, index):
        # type: (Live.Scene.Scene, int) -> None
        scene = self.get_optional_scene(live_scene)
        if scene is None:
            scene = Scene(live_scene, index=index, song=self._song)
        else:
            scene.index = index

        self.add_scene(scene)

    def _sort_scenes(self):
        # type: () -> None
        sorted_dict = collections.OrderedDict()
        for scene in SongFacade.live_song().scenes:
            sorted_dict[scene._live_ptr] = self.get_scene(scene)
        self._live_scene_id_to_scene = sorted_dict

    def _on_track_added_event(self, _):
        # type: (TrackAddedEvent) -> Sequence
        empty_scenes = []
        seq = Sequence()
        for scene in list(reversed(SongFacade.scenes()))[1:]:
            if scene.length == 0:
                empty_scenes.append(scene)
            else:
                break

        seq.add([scene.delete for scene in empty_scenes])
        return seq.done()

    def _on_song_started_event(self, _):
        # type: (SongStartedEvent) -> None
        # launch selected scene by clicking on play song
        if not self._track_recorder_service.is_recording and ApplicationView.is_session_view_active() and not SongFacade.selected_scene().has_playing_clips:
            self._song.stop_all_clips(quantized=False)
            self._song.stop_playing()
            SongFacade.selected_scene().fire()

    def scroll_scenes(self, go_next):
        # type: (bool) -> None
        scroll_values(SongFacade.scenes(), SongFacade.selected_scene(), go_next, rotate=False).select()

    def scroll_duplicate_scene_bar_lengths(self, go_next):
        # type: (bool) -> None
        selected_scene = SongFacade.selected_scene()
        if selected_scene.bar_length < 2:
            raise Protocol0Warning(
                "Cannot partial duplicate scene with bar length %s (min 2 bars)" % selected_scene.bar_length)

        bar_lengths = []
        power = 0
        while pow(2, power) <= selected_scene.bar_length / 2:
            bar_lengths += [pow(2, power), selected_scene.bar_length - pow(2, power)]
            power += 1
        bar_lengths = list(dict.fromkeys(bar_lengths))
        bar_lengths.sort()

        if self.selected_duplicate_scene_bar_length not in bar_lengths:
            self.selected_duplicate_scene_bar_length = 1
        self.selected_duplicate_scene_bar_length = scroll_values(
            bar_lengths, self.selected_duplicate_scene_bar_length, go_next
        )
        StatusBar.show_message("SCENE DUPLICATE : %s bars" % self.selected_duplicate_scene_bar_length)
        DomainEventBus.notify(SelectedDuplicateSceneBarLengthUpdatedEvent())
