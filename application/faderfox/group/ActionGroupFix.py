from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.audit.AudioLatencyAnalyzer import AudioLatencyAnalyzer
from protocol0.domain.audit.SetFixerManager import SetFixerManager
from protocol0.domain.audit.SetUpgradeManager import SetUpgradeManager
from protocol0.domain.lom.validation.ValidatorManager import ValidatorManager
from protocol0.shared.Logger import Logger
from protocol0.shared.SongFacade import SongFacade


class ActionGroupFix(ActionGroupMixin):
    CHANNEL = 5

    def configure(self):
        # type: () -> None
        # SET encoder
        self.add_encoder(identifier=1, name="refresh set appearance",
                         on_press=self._container.get(SetFixerManager).fix)

        # TRaCK encoder
        self.add_encoder(identifier=2, name="fix current track",
                         filter_active_tracks=True,
                         on_press=lambda: self._container.get(ValidatorManager).fix_object(SongFacade.current_track))

        # DEVice encoder
        self.add_encoder(identifier=3, name="Delete unnecessary devices",
                         on_press=self._container.get(SetUpgradeManager).delete_unnecessary_devices)

        # TAIL encoder
        self.add_encoder(identifier=4, name="add clip tail tracks",
                         on_press=self._container.get(SetUpgradeManager).update_external_synth_tracks_add_clip_tails)

        # USAMo encoder
        self.add_encoder(identifier=13, name="check usamo latency", on_press=self._container.get(AudioLatencyAnalyzer).test_audio_latency)

        # CLR encoder
        self.add_encoder(identifier=16, name="clear logs", on_press=Logger.clear)
