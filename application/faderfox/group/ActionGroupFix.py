from typing import Any

from protocol0.application.faderfox.group.AbstractActionGroup import AbstractActionGroup


class ActionGroupFix(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupFix, self).__init__(channel=5, *a, **k)
        # SET encoder
        self.add_encoder(identifier=1, name="refresh set appearance",
                         on_press=self.parent.setFixerManager.fix)

        # TRaCK encoder
        self.add_encoder(identifier=2, name="fix current track",
                         filter_active_tracks=True,
                         on_press=lambda: self.parent.validatorManager.fix_object(self.song.current_track))

        # DEVice encoder
        self.add_encoder(identifier=3, name="Delete unnecessary devices",
                         on_press=self.parent.setUpgradeManager.delete_unnecessary_devices)

        # TAIL encoder
        self.add_encoder(identifier=4, name="add clip tail tracks",
                         on_press=self.parent.setUpgradeManager.update_external_synth_tracks_add_clip_tails)

        # USAMo encoder
        self.add_encoder(identifier=13, name="check usamo latency", on_press=self.parent.audioLatencyAnalyzer.test_audio_latency)

        # CLR encoder
        self.add_encoder(identifier=16, name="clear logs", on_press=self.parent.logManager.clear)