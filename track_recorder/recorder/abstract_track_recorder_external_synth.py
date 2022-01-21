from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.track_recorder.recorder.abstract_track_recorder import AbstractTrackRecorder


class AbstractTrackRecorderExternalSynth(AbstractTrackRecorder):
    def __init__(self, track):
        # type: (ExternalSynthTrack) -> None
        super(AbstractTrackRecorderExternalSynth, self).__init__(track=track)
        self.track = track

    def _post_record(self):
        # type: () -> None
        self.track.instrument.activate_editor_automation()
        self.system.hide_plugins()
        # this is delayed in the case an encoder is touched after the recording is finished by mistake
        self.parent.wait([1, 10, 100], self.song.re_enable_automation)

        midi_clip = self.track.midi_track[self.recording_scene_index].clip
        audio_clip = self.track.audio_track[self.recording_scene_index].clip
        if not midi_clip or not audio_clip:
            return None

        audio_clip.clip_name.update(base_name=midi_clip.clip_name.base_name)

        midi_clip.select()
        midi_clip.show_loop()
