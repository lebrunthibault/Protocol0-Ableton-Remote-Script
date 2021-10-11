from typing import Any

from protocol0.components.action_groups.AbstractActionGroup import AbstractActionGroup
from protocol0.lom.clip.MidiClip import MidiClip
from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class ActionGroupTest(AbstractActionGroup):
    """ Just a playground to launch test actions """

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(ActionGroupTest, self).__init__(channel=0, *a, **k)
        # 1 encoder
        self.add_encoder(identifier=1, name="test", on_press=self.action_test)

    def action_test(self):
        # type: () -> None
        track = self.song.current_track
        self.parent.log_dev(track)
        if isinstance(track, ExternalSynthTrack):
            clip = track.midi_track.playable_clip  # type: MidiClip
            self.parent.log_dev(clip)
            clip.scale_velocities()
