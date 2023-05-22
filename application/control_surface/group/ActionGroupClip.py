from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.shared.Song import Song


class ActionGroupClip(ActionGroupInterface):
    CHANNEL = 7

    def configure(self):
        # type: () -> None
        # DUPLicate clip
        self.add_encoder(
            identifier=1,
            name="duplicate clip",
            on_press=lambda: Song.selected_track(SimpleMidiTrack).broadcast_selected_clip,
        )

        # midi clip to MONO
        self.add_encoder(
            identifier=4,
            name="midi clip to mono",
            on_press=lambda: Song.selected_clip(MidiClip).to_mono,
        )

        # BACK to previous file path
        self.add_encoder(
            identifier=13,
            name="set clip previous file path",
            on_press=lambda: partial(
                Song.selected_track(SimpleAudioTrack).back_to_previous_clip_file_path,
                Song.selected_clip(AudioClip),
            ),
        )
