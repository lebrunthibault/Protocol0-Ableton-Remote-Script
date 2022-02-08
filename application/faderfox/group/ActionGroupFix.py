from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.audit.AudioLatencyAnalyzerService import AudioLatencyAnalyzerService
from protocol0.domain.audit.SetFixerService import SetFixerService
from protocol0.domain.audit.SetUpgradeService import SetUpgradeService
from protocol0.domain.lom.validation.ValidatorService import ValidatorService
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class ActionGroupFix(ActionGroupMixin):
    CHANNEL = 5

    def configure(self):
        # type: () -> None
        # SET encoder
        self.add_encoder(identifier=1, name="refresh set appearance",
                         on_press=self._container.get(SetFixerService).fix)

        # TRaCK encoder
        self.add_encoder(identifier=2, name="fix current track",
                         filter_active_tracks=True,
                         on_press=lambda: self._container.get(ValidatorService).fix_object(SongFacade.current_track))

        # DEVice encoder
        self.add_encoder(identifier=3, name="Delete unnecessary devices",
                         on_press=self._container.get(SetUpgradeService).delete_unnecessary_devices)

        # TAIL encoder
        self.add_encoder(identifier=4, name="add clip tail tracks",
                         on_press=self._container.get(SetUpgradeService).update_external_synth_tracks_add_clip_tails)

        # USAMo encoder
        self.add_encoder(identifier=13, name="check usamo latency", on_press=self._container.get(AudioLatencyAnalyzerService).test_audio_latency)

        # CLR encoder
        self.add_encoder(identifier=16, name="clear logs", on_press=Logger.clear)
