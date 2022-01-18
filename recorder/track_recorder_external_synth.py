from typing import Optional

from protocol0.devices.InstrumentProphet import InstrumentProphet
from protocol0.recorder.abstract_track_recorder_external_synth import AbstractTrackRecorderExternalSynth
from protocol0.sequence.Sequence import Sequence


class TrackRecorderExternalSynth(AbstractTrackRecorderExternalSynth):
    @property
    def next_empty_clip_slot_index(self):
        # type: () -> Optional[int]
        for i in range(self.song.selected_scene.index, len(self.song.scenes)):
            if not self.track.midi_track.clip_slots[i].clip and not self.track.audio_track.clip_slots[i].clip:
                return i
        return None

    def pre_record(self):
        # type: () -> None
        self.track.solo = False
        if len(list(filter(None, [t.is_hearable for t in self.song.abstract_tracks]))) > 1:
            self.song.metronome = False
        self.track.midi_track.select()
        self.parent.navigationManager.show_device_view()
        if isinstance(self.track.instrument, InstrumentProphet) and not InstrumentProphet.EDITOR_DEVICE_ON:
            self.parent.defer(self.system.show_plugins)

    def on_record_cancelled(self):
        # type: () -> Sequence
        self.track.midi_track.playable_clip_slot.delete_clip()
        if self.track.audio_tail_track:
            self.track.audio_tail_track.playable_clip_slot.delete_clip()
        return self.track.audio_track.playable_clip_slot.delete_clip()
