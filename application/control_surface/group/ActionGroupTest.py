from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.audit.AudioLatencyAnalyzerService import AudioLatencyAnalyzerService
from protocol0.domain.audit.SetProfilingService import SetProfilingService
from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ActionGroupTest(ActionGroupInterface):
    CHANNEL = 16

    def configure(self):
        # type: () -> None
        # TEST encoder
        self.add_encoder(
            identifier=1,
            name="test",
            on_press=self.action_test,
        )

        # PROFiling encoder
        self.add_encoder(
            identifier=2,
            name="start set launch time profiling",
            on_press=self._container.get(SetProfilingService).profile_set,
        )

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=Logger.clear)

        # DUPLication encoder
        self.add_encoder(
            identifier=4, name="test server duplication", on_press=Backend.client().test_duplication
        )

        # USAMo encoder
        self.add_encoder(
            identifier=13,
            name="check usamo latency",
            on_press=lambda: partial(
                self._container.get(AudioLatencyAnalyzerService).test_audio_latency,
                Song.current_external_synth_track(),
            ),
        )

    def action_test(self):
        # type: () -> None
        if isinstance(Song.selected_clip(), AudioClip):
            Logger.dev(Song.selected_track(SimpleAudioTrack).file_path_mapping.get(Song.selected_clip().file_path, None))
            # Logger.dev("previous file path: %s" % (Song.selected_clip().previous_file_path is not None))
            Logger.dev()
        else:
            Logger.dev(Song.selected_clip().hash)
