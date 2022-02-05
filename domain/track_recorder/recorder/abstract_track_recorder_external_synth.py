from protocol0.domain.ApplicationView import ApplicationView
from protocol0.domain.lom.instrument.instrument.InstrumentProphet import InstrumentProphet
from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder
from protocol0.infra.System import System


class AbstractTrackRecorderExternalSynth(AbstractTrackRecorder):
    def __init__(self, track):
        # type: (ExternalSynthTrack) -> None
        super(AbstractTrackRecorderExternalSynth, self).__init__(track=track)
        self.track = track

    @property
    def _main_recording_track(self):
        # type: () -> SimpleTrack
        return self.track.midi_track

    def _pre_record(self):
        # type: () -> None
        self.track.midi_track.select()
        ApplicationView.show_device()
        if isinstance(self.track.instrument, InstrumentProphet) and not InstrumentProphet.EDITOR_DEVICE_ON:
            self.parent.defer(System.get_instance().show_plugins)

    def _post_record(self):
        # type: () -> None
        self.track.instrument.activate_editor_automation()
        System.get_instance().hide_plugins()
        # this is delayed in the case an encoder is touched after the recording is finished by mistake
        self.parent.wait([1, 10, 50, 100], self.song.re_enable_automation)

        midi_clip = self.track.midi_track.clip_slots[self.recording_scene_index].clip
        audio_clip = self.track.audio_track.clip_slots[self.recording_scene_index].clip
        if not midi_clip or not audio_clip:
            return None

        audio_clip.clip_name.update(base_name=midi_clip.clip_name.base_name)

        midi_clip.select()
        midi_clip.show_loop()