from protocol0.domain.track_recorder.external_synth.TrackRecorderExternalSynthAudioExport import \
    TrackRecorderExternalSynthAudioExport
from protocol0.shared.sequence.Sequence import Sequence


class TrackRecorderExternalSynthAudioExportOnce(TrackRecorderExternalSynthAudioExport):
    def legend(self, bar_length):
        # type: (int) -> str
        return "audio export once %s bars" % str(bar_length)

    def record(self, bar_length):
        # type: (float) -> Sequence
        # bypass recording twice
        return super(TrackRecorderExternalSynthAudioExportOnce, self).record(bar_length / 2)
