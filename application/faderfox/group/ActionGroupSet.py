from protocol0.application.faderfox.InterfaceState import InterfaceState
from protocol0.application.faderfox.group.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.lom.instrument.instrument.InstrumentProphet import InstrumentProphet
from protocol0.shared.AccessSong import AccessSong
from protocol0.shared.SongFacade import SongFacade


class ActionGroupSet(ActionGroupMixin, AccessSong):
    CHANNEL = 3

    def configure(self):
        # type: () -> None
        # SPLiT encoder
        self.add_encoder(identifier=1,
                         name="split scene",
                         on_scroll=InterfaceState.scroll_duplicate_scene_bar_lengths,
                         on_press=lambda: SongFacade.selected_scene().split
                         )

        # TAP tempo encoder
        self.add_encoder(identifier=2, name="tap tempo",
                         on_press=self._song.tap_tempo,
                         on_scroll=self._song.scroll_tempo
                         )

        # STATs encoder
        self.add_encoder(identifier=4, name="display song stats",
                         on_press=self._container.song_stats_manager.display_song_stats)

        # REV2 encoder
        self.add_encoder(identifier=5, name="rev2 toggle vst editor",
                         on_press=InstrumentProphet.toggle_editor_plugin_on)

        # VELO encoder
        self.add_encoder(identifier=13, name="smooth selected clip velocities",
                         on_scroll=lambda: SongFacade.selected_midi_clip().scale_velocities)

        # VOL encoder
        self.add_encoder(identifier=14, name="scroll all tracks volume",
                         on_scroll=self._container.mixing_manager.scroll_all_tracks_volume)

        # Session2ARrangement encoder
        self.add_encoder(identifier=16, name="bounce session to arrangement",
                         on_press=self._container.session_to_arrangement_manager.bounce_session_to_arrangement)
