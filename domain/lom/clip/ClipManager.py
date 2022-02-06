from typing import cast

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.shared.SongFacade import SongFacade
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning


class ClipManager(object):
    def smooth_selected_clip_velocities(self, go_next):
        # type: (bool) -> None
        clip = SongFacade.selected_clip
        if not clip:
            raise Protocol0Warning("No selected clip, cannot scale velocities")

        if not isinstance(clip, MidiClip):
            raise Protocol0Warning("selected clip is not a midi clip, cannot scale velocities")

        clip = cast(MidiClip, clip)
        clip.scale_velocities(go_next=go_next, scaling_factor=4)
