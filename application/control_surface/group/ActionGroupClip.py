from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.track.simple_track.SimpleMidiTrack import SimpleMidiTrack
from protocol0.shared.SongFacade import SongFacade


class ActionGroupClip(ActionGroupInterface):
    CHANNEL = 7

    def configure(self):
        # type: () -> None
        # DUPLicate clip encoder
        self.add_encoder(
            identifier=1,
            name="duplicate clip",
            on_press=lambda: SongFacade.selected_track(SimpleMidiTrack).duplicate_selected_clip,
        )

        # midi clip to MONO encoder
        self.add_encoder(
            identifier=4,
            name="midi clip to mono",
            on_press=lambda: SongFacade.selected_clip(MidiClip).to_mono,
        )