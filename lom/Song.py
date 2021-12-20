from functools import partial

from typing import List, Optional, Any, Iterator

import Live
from protocol0.components.SongDataManager import save_song_data
from protocol0.config import Config
from protocol0.devices.InstrumentProphet import InstrumentProphet
from protocol0.enums.SongLoadStateEnum import SongLoadStateEnum
from protocol0.lom.AbstractObject import AbstractObject
from protocol0.lom.Scene import Scene
from protocol0.lom.SongActionMixin import SongActionMixin
from protocol0.lom.clip.AudioClip import AudioClip
from protocol0.lom.clip.Clip import Clip
from protocol0.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.lom.device.DeviceParameter import DeviceParameter
from protocol0.lom.track.AbstractTrack import AbstractTrack
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.sequence.Sequence import Sequence
from protocol0.utils.decorators import p0_subject_slot, debounce
from protocol0.utils.utils import find_if


class Song(SongActionMixin, AbstractObject):
    __subject_events__ = ("session_end",)

    def __init__(self, song, *a, **k):
        # type: (Live.Song.Song, Any, Any) -> None
        super(Song, self).__init__(*a, **k)
        self._song = song
        self._view = self._song.view  # type: Live.Song.Song.View

        # Global accessible objects / object mappings
        self.usamo_track = None  # type: Optional[SimpleTrack]
        self.master_track = None  # type: Optional[SimpleTrack]
        self.template_dummy_clip = None  # type: Optional[AudioClip]
        self.midi_recording_quantization_checked = False

        self.errored = False
        self.song_load_state = SongLoadStateEnum.PRE_LOAD
        self._is_playing_listener.subject = self._song
        self._record_mode_listener.subject = self._song
        self.session_end_listener.subject = self
        self._tempo_listener.subject = self._song
        self._midi_recording_quantization_listener.subject = self._song

    def __call__(self):
        # type: () -> Live.Song.Song
        """ allows for self.song() behavior to extend other surface script classes """
        return self.parent.song()

    @p0_subject_slot("is_playing")
    def _is_playing_listener(self):
        # type: () -> None
        if not self.is_playing:
            # noinspection PyUnresolvedReferences
            self.notify_session_end()
            # if not self.song.selected_scene.is
            Config.CURRENT_RECORD_TYPE = None
            if self.song.playing_scene:
                self.parent.defer(self.song.playing_scene.mute_audio_tails)
            return

        # song started playing
        if not self.application.session_view_active or Config.CURRENT_RECORD_TYPE is not None:
            return
        # launch selected scene by clicking on play song
        if not self.song.selected_scene.has_playing_clips:
            self.song.stop_playing()
            self.song.selected_scene.fire()
        else:
            self.song.selected_scene._is_triggered_listener()

    @p0_subject_slot("record_mode")
    def _record_mode_listener(self):
        # type: () -> None
        pass

    @p0_subject_slot("session_end")
    def session_end_listener(self):
        # type: () -> None
        pass

    @p0_subject_slot("tempo")
    @debounce(wait_time=60)  # 1 second
    def _tempo_listener(self):
        # type: () -> None
        self.midi_recording_quantization_checked = False
        self.parent.songDataManager.save()
        self.parent.defer(partial(setattr, self, "tempo", round(self.tempo)))

    @p0_subject_slot("midi_recording_quantization")
    @save_song_data
    def _midi_recording_quantization_listener(self):
        # type: () -> None
        pass

    # TRACKS

    @property
    def all_simple_tracks(self):
        # type: () -> Iterator[SimpleTrack]
        return self.parent.songTracksManager.all_simple_tracks

    @property
    def simple_tracks(self):
        # type: () -> Iterator[SimpleTrack]
        return (track for track in self.all_simple_tracks if track.IS_ACTIVE)

    @property
    def abstract_tracks(self):
        # type: () -> Iterator[AbstractTrack]
        for track in self.simple_tracks:
            if isinstance(track, SimpleInstrumentBusTrack) or track == self.song.usamo_track:
                continue
            if isinstance(track.abstract_track, NormalGroupTrack) and track != track.abstract_track.base_track:
                yield track
            elif track == track.abstract_track.base_track:
                yield track.abstract_track

    @property
    def external_synth_tracks(self):
        # type: () -> Iterator[ExternalSynthTrack]
        for track in self.abstract_tracks:
            if isinstance(track, ExternalSynthTrack):
                yield track

    @property
    def prophet_tracks(self):
        # type: () -> Iterator[ExternalSynthTrack]
        for track in self.external_synth_tracks:
            if isinstance(track.instrument, InstrumentProphet):
                yield track

    @property
    def armed_tracks(self):
        # type: () -> Iterator[AbstractTrack]
        return (track for track in self.abstract_tracks if track.is_armed)

    @property
    def visible_tracks(self):
        # type: () -> Iterator[SimpleTrack]
        return (t for t in self.simple_tracks if t.is_visible)

    @property
    def scrollable_tracks(self):
        # type: () -> Iterator[AbstractTrack]
        for track in self.abstract_tracks:
            if not track.is_visible:
                continue
            # when a group track is unfolded, will directly select the first sub_trackB
            if isinstance(track, NormalGroupTrack) and not track.is_folded:
                continue
            yield track

    @property
    def selected_track(self):
        # type: () -> Optional[SimpleTrack]
        return self.parent.songTracksManager.get_optional_simple_track(self.song._view.selected_track)

    @property
    def current_track(self):
        # type: () -> AbstractTrack
        return self.song.selected_track.abstract_track

    # SCENES

    @property
    def scenes(self):
        # type: () -> List[Scene]
        return self.parent.songScenesManager.scenes

    @property
    def selected_scene(self):
        # type: () -> Scene
        return self.parent.songScenesManager.get_scene(self.song._view.selected_scene)

    @selected_scene.setter
    def selected_scene(self, scene):
        # type: (Scene) -> None
        self.song._view.selected_scene = scene._scene

    @property
    def playing_scene(self):
        # type: () -> Optional[Scene]
        return Scene.PLAYING_SCENE

    @property
    def looping_scene(self):
        # type: () -> Optional[Scene]
        return Scene.LOOPING_SCENE

    # CLIP SLOTS

    @property
    def highlighted_clip_slot(self):
        # type: () -> Optional[ClipSlot]
        return next((cs for cs in self.song.selected_track.clip_slots if cs._clip_slot == self.song._view.highlighted_clip_slot), None)

    @highlighted_clip_slot.setter
    def highlighted_clip_slot(self, clip_slot):
        # type: (ClipSlot) -> None
        self.song._view.highlighted_clip_slot = clip_slot._clip_slot

    # CLIPS

    @property
    def selected_clip(self):
        # type: () -> Optional[Clip]
        return self.highlighted_clip_slot and self.highlighted_clip_slot.clip

    @selected_clip.setter
    def selected_clip(self, selected_clip):
        # type: (Clip) -> None
        self.highlighted_clip_slot = selected_clip.clip_slot

    @property
    def selected_parameter(self):
        # type: () -> Optional[DeviceParameter]
        all_parameters = [param for track in self.simple_tracks for param in track.device_parameters]
        return find_if(lambda p: p._device_parameter == self.song._view.selected_parameter, all_parameters)

    @property
    def is_playing(self):
        # type: () -> bool
        return self._song.is_playing

    @is_playing.setter
    def is_playing(self, is_playing):
        # type: (bool) -> None
        self._song.is_playing = is_playing

    @property
    def metronome(self):
        # type: () -> float
        return self._song.metronome

    @metronome.setter
    def metronome(self, metronome):
        # type: (bool) -> None
        self._song.metronome = metronome

    @property
    def current_song_time(self):
        # type: () -> None
        if self._song:
            return self._song.current_song_time

    @property
    def tempo(self):
        # type: () -> float
        return self._song.tempo

    @tempo.setter
    def tempo(self, tempo):
        # type: (float) -> None
        try:
            self._song.tempo = tempo
        except RuntimeError:
            pass

    @property
    def signature_numerator(self):
        # type: () -> int
        return self._song.signature_numerator

    @property
    def signature_denominator(self):
        # type: () -> int
        return self._song.signature_denominator

    def get_current_beats_song_time(self):
        # type: () -> Live.Song.BeatTime
        return self._song.get_current_beats_song_time()

    @property
    def clip_trigger_quantization(self):
        # type: () -> int
        return self._song.clip_trigger_quantization

    @clip_trigger_quantization.setter
    def clip_trigger_quantization(self, clip_trigger_quantization):
        # type: (int) -> None
        self._song.clip_trigger_quantization = clip_trigger_quantization

    @property
    def midi_recording_quantization(self):
        # type: () -> int
        return self._song.midi_recording_quantization

    @midi_recording_quantization.setter
    def midi_recording_quantization(self, midi_recording_quantization):
        # type: (int) -> None
        if self._song:
            self._song.midi_recording_quantization = midi_recording_quantization

    @property
    def tempo_default_midi_recording_quantization(self):
        # type: () -> Any
        if self.tempo < Config.SPLIT_QUANTIZATION_TEMPO:
            return Live.Song.RecordingQuantization.rec_q_sixtenth
        else:
            return Live.Song.RecordingQuantization.rec_q_eight

    @property
    def session_record_status(self):
        # type: () -> int
        return self._song.session_record_status

    @property
    def session_record(self):
        # type: () -> bool
        return self._song.session_record

    @session_record.setter
    def session_record(self, session_record):
        # type: (bool) -> None
        self._song.session_record = session_record

    def global_record(self):
        # type: () -> Sequence
        seq = Sequence()
        self.record_mode = True
        seq.add(wait=1)
        seq.add(complete_on=self._record_mode_listener, no_timeout=True)
        return seq.done()

    @property
    def record_mode(self):
        # type: () -> bool
        return self._song.record_mode

    @record_mode.setter
    def record_mode(self, record_mode):
        # type: (bool) -> None
        self._song.record_mode = record_mode

    @property
    def session_automation_record(self):
        # type: () -> bool
        return self._song.session_automation_record

    @session_automation_record.setter
    def session_automation_record(self, session_automation_record):
        # type: (bool) -> None
        self._song.session_automation_record = session_automation_record

    def scrub_by(self, beat_offset):
        # type: (float) -> None
        if self._song:
            self._song.scrub_by(beat_offset)
