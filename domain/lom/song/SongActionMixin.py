from functools import partial

from typing import TYPE_CHECKING, Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.scene.ScenesMappedEvent import ScenesMappedEvent
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.utils import scroll_values
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.song.Song import Song


# noinspection PyTypeHints,PyArgumentList,PyAttributeOutsideInit
class SongActionMixin(object):
    def reset(self):
        # type: (Song) -> None
        """ stopping immediately """
        self.stop_playing()
        # noinspection PyPropertyAccess
        self._song.current_song_time = 0
        self.stop_all_clips()

    def play_pause(self):
        # type: (Song) -> None
        if self.is_playing:
            self.reset()
        else:
            self.start_playing()

    def continue_playing(self):
        # type: (Song) -> None
        if self._song:
            self._song.continue_playing()

    def re_enable_automation(self):
        # type: (Song) -> None
        self._song.re_enable_automation()

    def start_playing(self):
        # type: (Song) -> None
        self._song.is_playing = True

    def stop_playing(self):
        # type: (Song) -> None
        self._song.stop_playing()

    def stop_all_clips(self, quantized=True):
        # type: (Song, bool) -> None
        # noinspection PyTypeChecker
        self._song.stop_all_clips(quantized)

    def begin_undo_step(self):
        # type: (Song) -> None
        self._song.begin_undo_step()

    def end_undo_step(self):
        # type: (Song) -> None
        self._song.end_undo_step()

    def undo(self):
        # type: (Song) -> None
        self._song.undo()

    def select_track(self, abstract_track):
        # type: (Song, AbstractTrack) -> Sequence
        if abstract_track.group_track:
            abstract_track.group_track.is_folded = False
        seq = Sequence()
        if SongFacade.selected_track() != abstract_track.base_track:
            self._view.selected_track = abstract_track._track
            seq.defer()
        return seq.done()

    def unfocus_all_tracks(self):
        # type: (Song) -> None
        self._unsolo_all_tracks()
        self._unarm_all_tracks()

    def _unarm_all_tracks(self):
        # type: (Song) -> None
        for t in SongFacade.partially_armed_tracks():
            if t.abstract_track != SongFacade.current_track():
                t.unarm()

    def _unsolo_all_tracks(self):
        # type: (Song) -> None
        for t in SongFacade.abstract_tracks():
            if t.solo and t != SongFacade.current_track():
                t.solo = False

    def create_midi_track(self, index):
        # type: (Song, int) -> Sequence
        seq = Sequence()
        self._song.create_midi_track(Index=index)
        seq.wait_for_event(TracksMappedEvent)
        return seq.done()

    def duplicate_track(self, index):
        # type: (Song, int) -> Sequence
        seq = Sequence()
        self._song.duplicate_track(index)
        seq.wait_for_event(TracksMappedEvent)
        return seq.done()

    def delete_track(self, index):
        # type: (Song, int) -> Sequence
        seq = Sequence()
        self._song.delete_track(index)
        seq.wait_for_event(TracksMappedEvent)
        return seq.done()

    def scroll_tracks(self, go_next):
        # type: (bool) -> None
        if not SongFacade.selected_track().IS_ACTIVE:
            next(SongFacade.simple_tracks()).select()
            return None

        next_track = scroll_values(SongFacade.scrollable_tracks(), SongFacade.current_track(), go_next, rotate=False)
        if next_track:
            next_track.select()

    def duplicate_scene(self, index):
        # type: (Song, int) -> Sequence
        seq = Sequence()
        seq.add(partial(self._song.duplicate_scene, index))
        seq.wait_for_event(ScenesMappedEvent)
        return seq.done()

    def create_scene(self, scene_index=None):
        # type: (Song, Optional[int]) -> Sequence
        seq = Sequence()
        scenes_count = len(SongFacade.scenes())
        seq.add(partial(self._song.create_scene, scene_index or scenes_count))
        seq.wait_for_event(ScenesMappedEvent)
        seq.defer()
        return seq.done()

    def delete_scene(self, scene_index):
        # type: (Song, Optional) -> Optional[Sequence]
        if len(SongFacade.scenes()) == 1:
            Logger.warning("Cannot delete last scene")
            return None

        seq = Sequence()
        seq.add(partial(self._song.delete_scene, scene_index))
        seq.wait_for_event(ScenesMappedEvent)
        seq.defer()
        return seq.done()

    def select_device(self, track, device):
        # type: (Song, SimpleTrack, Device) -> Sequence
        seq = Sequence()
        seq.add(track.select)
        seq.add(partial(self._view.select_device, device._device))
        seq.add(ApplicationViewFacade.focus_detail)
        return seq.done()

    def scroll_scenes(self, go_next):
        # type: (bool) -> None
        scroll_values(SongFacade.scenes(), SongFacade.selected_scene(), go_next, rotate=False).select()

    def tap_tempo(self):
        # type: (Song) -> None
        self._song.tap_tempo()

    def scroll_tempo(self, go_next):
        # type: (Song, bool) -> None
        increment = 1 if go_next else -1
        self.tempo += increment

    def check_midi_recording_quantization(self):
        # type: (Song) -> Optional[Sequence]
        if self._midi_recording_quantization_checked or self.midi_recording_quantization == self.tempo_default_midi_recording_quantization:
            return None

        self._midi_recording_quantization_checked = True
        seq = Sequence()
        seq.prompt("Midi recording quantization %s is not tempo default : %s, Set to default ?" % (
            self.midi_recording_quantization, self.tempo_default_midi_recording_quantization))
        seq.add(
            partial(setattr, self, "midi_recording_quantization", self.tempo_default_midi_recording_quantization))
        seq.add(partial(StatusBar.show_message,
                        "Quantization set to %s" % self.tempo_default_midi_recording_quantization))

        return seq.done()
