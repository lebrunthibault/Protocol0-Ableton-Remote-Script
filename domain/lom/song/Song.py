from functools import partial

from typing import Optional, Any, Iterator

import Live
from protocol0.domain.lom.UseFrameworkEvents import UseFrameworkEvents
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipEnveloppeShowedEvent import ClipEnveloppeShowedEvent
from protocol0.domain.lom.clip.ClipSelectedEvent import ClipSelectedEvent
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.song.SongActionMixin import SongActionMixin
from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleInstrumentBusTrack import SimpleInstrumentBusTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.decorators import p0_subject_slot, debounce
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils import find_if
from protocol0.shared.Config import Config
from protocol0.shared.SongFacade import SongFacade


class Song(SongActionMixin, UseFrameworkEvents):
    def __init__(self, song):
        # type: (Live.Song.Song) -> None
        super(Song, self).__init__()
        self._song = song
        self._view = self._song.view  # type: Live.Song.Song.View

        # Global accessible objects / object mappings
        self._midi_recording_quantization_checked = False
        self._is_playing = False  # caching this because _is_playing_listener activates multiple times

        self.is_playing_listener.subject = self._song
        self._tempo_listener.subject = self._song

        DomainEventBus.subscribe(ClipEnveloppeShowedEvent, lambda _: self.re_enable_automation())
        DomainEventBus.subscribe(ClipSelectedEvent, self._on_selected_clip_event)

    # def __call__(self):
    #     # type: () -> Live.Song.Song
    #     """ allows for self.song() behavior to extend other surface script classes """
    #     return self.container.song()

    @p0_subject_slot("is_playing")
    def is_playing_listener(self):
        # type: () -> None
        # deduplicate calls with is_playing True
        if self.is_playing == self._is_playing:
            return
        else:
            self._is_playing = self.is_playing

        if not self.is_playing:
            DomainEventBus.notify(SongStoppedEvent())
            Config.CURRENT_RECORD_TYPE = None
            if SongFacade.playing_scene():
                Scheduler.defer(SongFacade.playing_scene().mute_audio_tails)
            return
        else:
            DomainEventBus.notify(SongStartedEvent())

    @p0_subject_slot("tempo")
    @debounce(wait_time=60)  # 1 second
    def _tempo_listener(self):
        # type: () -> None
        self._midi_recording_quantization_checked = False
        Scheduler.defer(partial(setattr, self, "tempo", round(self.tempo)))

    # TRACKS

    @property
    def abstract_tracks(self):
        # type: () -> Iterator[AbstractTrack]
        for track in SongFacade.simple_tracks():
            if isinstance(track, SimpleInstrumentBusTrack) or track == SongFacade.usamo_track():
                continue
            if isinstance(track.abstract_track, NormalGroupTrack) and track != track.abstract_track.base_track:
                yield track
            elif track == track.abstract_track.base_track:
                yield track.abstract_track

    @property
    def scrollable_tracks(self):
        # type: () -> Iterator[AbstractTrack]
        for track in self.abstract_tracks:
            if not track.is_visible:
                continue
            # when a group track is unfolded, will directly select the first sub_trackB
            if isinstance(track, NormalGroupTrack) and not track.is_folded and isinstance(track.sub_tracks[0],
                                                                                          SimpleTrack):
                continue
            yield track

    # SCENES

    @property
    def selected_scene(self):
        # type: () -> Scene
        return SongFacade.selected_scene()

    @selected_scene.setter
    def selected_scene(self, scene):
        # type: (Scene) -> None
        self._view.selected_scene = scene._scene

    # CLIP SLOTS

    @property
    def highlighted_clip_slot(self):
        # type: () -> Optional[ClipSlot]
        return SongFacade.highlighted_clip_slot()

    @highlighted_clip_slot.setter
    def highlighted_clip_slot(self, clip_slot):
        # type: (ClipSlot) -> None
        self._view.highlighted_clip_slot = clip_slot._clip_slot

    # CLIPS

    @property
    def selected_clip(self):
        # type: () -> Optional[Clip]
        return SongFacade.selected_clip()

    @selected_clip.setter
    def selected_clip(self, selected_clip):
        # type: (Clip) -> None
        self.highlighted_clip_slot = selected_clip.clip_slot

    def _on_selected_clip_event(self, event):
        # type: (ClipSelectedEvent) -> None
        self.highlighted_clip_slot = event.clip.clip_slot

    @property
    def selected_parameter(self):
        # type: () -> Optional[DeviceParameter]
        all_parameters = [param for track in SongFacade.simple_tracks() for param in track.device_parameters]
        return find_if(lambda p: p._device_parameter == self._view.selected_parameter, all_parameters)

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
        # type: () -> bool
        return self._song.metronome

    @metronome.setter
    def metronome(self, metronome):
        # type: (bool) -> None
        self._song.metronome = metronome

    @property
    def loop(self):
        # type: () -> bool
        return self._song.loop

    @loop.setter
    def loop(self, loop):
        # type: (bool) -> None
        self._song.loop = loop

    @property
    def loop_start(self):
        # type: () -> float
        return self._song.loop_start

    @loop_start.setter
    def loop_start(self, loop_start):
        # type: (float) -> None
        self._song.loop_start = loop_start

    @property
    def loop_length(self):
        # type: () -> float
        return self._song.loop_length

    @loop_length.setter
    def loop_length(self, loop_length):
        # type: (float) -> None
        self._song.loop_length = loop_length

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
    def session_record(self):
        # type: () -> bool
        return self._song.session_record

    @session_record.setter
    def session_record(self, session_record):
        # type: (bool) -> None
        self._song.session_record = session_record

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
