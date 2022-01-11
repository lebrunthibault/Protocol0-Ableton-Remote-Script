from functools import partial

from typing import TYPE_CHECKING, Optional, Any

import Live
from protocol0.enums.AbstractEnum import AbstractEnum
from protocol0.enums.SongLoadStateEnum import SongLoadStateEnum
from protocol0.lom.device.Device import Device
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.utils import scroll_values

if TYPE_CHECKING:
    from protocol0.lom.Song import Song


# noinspection PyTypeHints,PyArgumentList
class SongActionMixin(object):
    def get_data(self, key, default_value=None):
        # type: (Song, str, Any) -> Any
        return self._song.get_data(key, default_value)

    def set_data(self, key, value):
        # type: (Song, str, Any) -> None
        if isinstance(value, AbstractEnum):
            value = value.value
        self._song.set_data(key, value)

    def activate_arrangement(self):
        # type: (Song) -> None
        self.parent.navigationManager.show_arrangement()
        self._song.back_to_arranger = False

    def reset(self, save_data=False):
        # type: (Song, bool) -> None
        """ stopping immediately """
        self.stop_playing()
        # noinspection PyPropertyAccess
        self._song.current_song_time = 0
        self.stop_all_clips()
        self.parent.wait(3, partial(setattr, self.song, "song_load_state", SongLoadStateEnum.LOADED))
        if save_data:
            self.parent.songDataManager.save()

    def play(self):
        # type: (Song) -> None
        if self.application.session_view_active:
            self.selected_scene.fire()
        else:
            self.is_playing = True  # play arrangement

    def continue_playing(self):
        # type: (Song) -> None
        if self._song:
            self._song.continue_playing()

    def enable_clip_trigger_quantization(self):
        # type: (Song) -> None
        self.clip_trigger_quantization = Live.Song.Quantization.q_bar

    def disable_clip_trigger_quantization(self):
        # type: (Song) -> None
        self.clip_trigger_quantization = Live.Song.Quantization.q_no_q

    def re_enable_automation(self):
        # type: (Song) -> None
        self._song.re_enable_automation()

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
        self.metronome = False
        self._song.undo()

    def select_track(self, abstract_track):
        # type: (Song, AbstractTrack) -> Sequence
        if abstract_track.group_track:
            abstract_track.group_track.is_folded = False
        seq = Sequence()
        if self.song.selected_track != abstract_track.base_track:
            self._view.selected_track = abstract_track._track
            seq.add(wait=1)
        return seq.done()

    def scroll_tracks(self, go_next):
        # type: (Song, bool) -> None
        if not self.song.selected_track.IS_ACTIVE:
            next(self.song.simple_tracks).select()
            return None

        next_track = scroll_values(self.scrollable_tracks, self.current_track, go_next, rotate=False)
        if next_track:
            next_track.select()
            if next_track == list(self.scrollable_tracks)[-1]:
                self.parent.sessionManager.toggle_session_ring()

    def unfocus_all_tracks(self):
        # type: (Song) -> Sequence
        self._unsolo_all_tracks()
        return self._unarm_all_tracks()

    def _unarm_all_tracks(self):
        # type: (Song) -> Sequence
        seq = Sequence()
        seq.add([t.unarm for t in self.armed_tracks])
        return seq.done()

    def _unsolo_all_tracks(self):
        # type: (Song) -> None
        for t in self.song.abstract_tracks:
            if t.solo and t != self.current_track:
                t.solo = False

    def duplicate_track(self, index):
        # type: (Song, int) -> Sequence
        seq = Sequence()
        seq.add(partial(self._song.duplicate_track, index), complete_on=self.parent.songTracksManager.tracks_listener)
        return seq.done()

    def delete_track(self, index):
        # type: (Song, int) -> Sequence
        seq = Sequence()
        seq.add(partial(self._song.delete_track, index), complete_on=self.parent.songTracksManager.tracks_listener)
        return seq.done()

    def duplicate_scene(self, index):
        # type: (Song, int) -> Sequence
        seq = Sequence()
        # seq.add(partial(self._song.duplicate_scene, index))
        seq.add(partial(self._song.duplicate_scene, index), complete_on=self.parent.songScenesManager.scenes_listener)
        return seq.done()

    def scroll_scenes(self, go_next):
        # type: (Song, bool) -> None
        scroll_values(self.scenes, self.selected_scene, go_next, rotate=False).select()

    def create_scene(self, scene_index=None):
        # type: (Song, Optional[int]) -> Sequence
        seq = Sequence()
        scenes_count = len(self.song.scenes)
        seq.add(partial(self._song.create_scene, scene_index or scenes_count), complete_on=self.parent.songScenesManager.scenes_listener)
        seq.add(wait=1)
        seq.add(lambda: self.parent.show_message("created !"))
        return seq.done()

    def delete_scene(self, scene_index):
        # type: (Song, Optional) -> Optional[Sequence]
        if len(self.song.scenes) == 1:
            self.parent.log_warning("Cannot delete last scene")
            return None

        seq = Sequence()
        seq.add(partial(self._song.delete_scene, scene_index), complete_on=self.parent.songScenesManager.scenes_listener)
        seq.add(wait=1)
        return seq.done()

    def select_device(self, device):
        # type: (Song, Device) -> Sequence
        seq = Sequence()
        seq.add(device.track.select)
        seq.add(partial(self._view.select_device, device._device))
        seq.add(self.parent.navigationManager.focus_detail)
        return seq.done()

    def tap_tempo(self):
        # type: (Song) -> None
        self._song.tap_tempo()

    def check_midi_recording_quantization(self):
        # type: (Song) -> Optional[Sequence]
        if self.midi_recording_quantization_checked or self.midi_recording_quantization == self.tempo_default_midi_recording_quantization:
            return None

        self.midi_recording_quantization_checked = True
        self.parent.songDataManager.save()
        seq = Sequence()
        seq.prompt("Midi recording quantization %s is not tempo default : %s, Set to default ?" % (
            self.midi_recording_quantization, self.tempo_default_midi_recording_quantization), no_cancel=True)
        seq.add(
            partial(setattr, self, "midi_recording_quantization", self.tempo_default_midi_recording_quantization))
        seq.add(partial(self.parent.show_message,
                        "Quantization set to %s" % self.tempo_default_midi_recording_quantization))

        return seq.done()
