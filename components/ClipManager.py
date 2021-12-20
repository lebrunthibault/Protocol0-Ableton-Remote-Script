from typing import cast

from protocol0.AbstractControlSurfaceComponent import AbstractControlSurfaceComponent
from protocol0.lom.clip.MidiClip import MidiClip


class ClipManager(AbstractControlSurfaceComponent):
    def smooth_selected_clip_velocities(self, go_next):
        # type: (bool) -> None
        clip = self.song.selected_clip
        if not clip:
            self.parent.show_message("No selected clip, cannot scale velocities")
            return

        if not isinstance(clip, MidiClip):
            self.parent.show_message("selected clip is not a midi clip, cannot scale velocities")
            return

        clip = cast(MidiClip, clip)
        clip.scale_velocities(go_next=go_next, scaling_factor=4)
