from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup


class ActionGroupData(AbstractActionGroup):
    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupData, self).__init__(channel=7, *a, **k)
        # SAVE encoder
        self.add_encoder(identifier=1, name="save song data", on_press=self.parent.songDataManager.save_song_and_tracks)

        # CLeaR encoder
        self.add_encoder(identifier=2, name="clear song data", on_press=self.parent.songDataManager.clear)
