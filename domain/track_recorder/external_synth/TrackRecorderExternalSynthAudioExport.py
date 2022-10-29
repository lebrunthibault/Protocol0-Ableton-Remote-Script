from functools import partial

from typing import Any, Optional

from protocol0.domain.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudio import \
    TrackRecorderExternalSynthAudio
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioExport(TrackRecorderExternalSynthAudio):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(TrackRecorderExternalSynthAudioExport, self).__init__(*a, **k)
        self._audio_file_path = None  # type: Optional[str]
        self._audio_tail_file_path = None  # type: Optional[str]

    def pre_record(self):
        # type: () -> Sequence
        audio_clip = self.track.audio_track.clip_slots[self.recording_scene_index].clip
        if audio_clip is not None:
            self._audio_file_path = audio_clip.file_path

        audio_tail_clip = self.track.audio_tail_track.clip_slots[self.recording_scene_index].clip
        if audio_tail_clip is not None:
            self._audio_tail_file_path = audio_tail_clip.file_path

        return super(TrackRecorderExternalSynthAudioExport, self).pre_record()

    def record(self, bar_length):
        # type: (float) -> Sequence
        self.track.audio_tail_track.arm_state.unarm()
        seq = Sequence()
        seq.add(partial(super(TrackRecorderExternalSynthAudioExport, self).record, bar_length))
        seq.add(self.track.audio_track.stop)
        seq.add(self.track.audio_tail_track.arm_state.arm)
        seq.add(partial(super(TrackRecorderExternalSynthAudioExport, self).record, bar_length))

        return seq.done()

    def legend(self, bar_length):
        # type: (int) -> str
        return "audio export %s bars" % str(bar_length)

    def post_record(self, bar_length):
        # type: (int) -> Optional[Sequence]
        super(TrackRecorderExternalSynthAudioExport, self).post_record(bar_length)
        self.track.audio_tail_track.clip_slots[self.recording_scene_index].clip.muted = False
        seq = Sequence()
        seq.wait(11)
        seq.add(self._rename_clips)
        seq.add(self._replace_clips)
        return seq.done()

    def _rename_clips(self):
        # type: () -> None
        self.track.audio_track.clip_slots[self.recording_scene_index].clip.clip_name.update("atk")
        self.track.audio_tail_track.clip_slots[self.recording_scene_index].clip.clip_name.update(
            "loop")

    def _replace_clips(self):
        # type: () -> None
        audio_tracks = [track for track in SongFacade.simple_tracks() if
                        isinstance(track, SimpleAudioTrack)]
        audio_clips = [clip for track in audio_tracks for clip in track.clips]

        if self._audio_file_path is not None:
            clips_to_replace = [clip for clip in audio_clips if
                                clip.file_path == self._audio_file_path]
            Logger.dev(clips_to_replace)
            for clip in audio_clips:
                if clip.file_path == self._audio_file_path:
                    pass

        if self._audio_tail_file_path is not None:
            for clip in audio_clips:
                if clip.file_path == self._audio_tail_file_path:
                    pass
