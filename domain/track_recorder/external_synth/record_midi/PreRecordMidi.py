from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import \
    ExternalSynthTrack
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface


class PreRecordMidi(RecordProcessorInterface):
    def process(self, track, _):
        # type: (ExternalSynthTrack, RecordConfig) -> None
        track.monitoring_state.monitor_midi()
