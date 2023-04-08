from functools import partial

from typing import cast

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.audit.AudioLatencyAnalyzerService import AudioLatencyAnalyzerService
from protocol0.domain.audit.SetProfilingService import SetProfilingService
from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ActionGroupTest(ActionGroupInterface):
    CHANNEL = 13

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

        self.add_encoder(identifier=5, name="log midi", on_press=self.action_log_midi)

        # USAMo encoder
        self.add_encoder(
            identifier=13,
            name="check usamo latency",
            on_press=lambda: partial(
                self._container.get(AudioLatencyAnalyzerService).test_audio_latency,
                Song.current_external_synth_track(),
            ),
        )

    def action_log_midi(self):
        # type: () -> None
        clip = Song.selected_clip()
        Logger.info("previous hash: %s" % clip.previous_hash)
        Logger.info("hash: %s" % clip.get_hash(Song.selected_track().devices.parameters))

        if isinstance(Song.selected_clip(), AudioClip):
            track = Song.selected_track(SimpleAudioTrack)
            Logger.info(track.clip_mapping._file_path_mapping)

    def action_test(self):
        # type: () -> None
        pass
