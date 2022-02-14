from functools import partial

from protocol0.application.control_surface.ActionGroupMixin import ActionGroupMixin
from protocol0.domain.audit.SongStatsService import SongStatsService
from protocol0.domain.lom.instrument.instrument.InstrumentProphet import InstrumentProphet
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.set.SessionToArrangementService import SessionToArrangementService
from protocol0.domain.lom.scene.ScenesService import SongScenesService
from protocol0.shared.SongFacade import SongFacade


class ActionGroupSet(ActionGroupMixin):
    CHANNEL = 3

    def configure(self):
        # type: () -> None
        # SPLiT encoder
        self.add_encoder(identifier=1,
                         name="split scene",
                         on_scroll=self._container.get(SongScenesService).scroll_duplicate_scene_bar_lengths,
                         on_press=lambda: partial(SongFacade.selected_scene().split, self._container.get(SongScenesService).selected_duplicate_scene_bar_length)
                         )

        # TAP tempo encoder
        self.add_encoder(identifier=2, name="tap tempo",
                         on_press=self._song.tap_tempo,
                         on_scroll=self._song.scroll_tempo
                         )

        # STATs encoder
        self.add_encoder(identifier=4, name="display song stats",
                         on_press=self._container.get(SongStatsService).display_song_stats)

        # REV2 encoder
        self.add_encoder(identifier=5, name="rev2 toggle vst editor",
                         on_press=InstrumentProphet.toggle_editor_plugin_on)

        # VELO encoder
        self.add_encoder(identifier=13, name="smooth selected clip velocities",
                         on_scroll=lambda: SongFacade.selected_midi_clip().scale_velocities)

        # VOL encoder
        self.add_encoder(identifier=14, name="scroll all tracks volume",
                         on_scroll=self._container.get(MixingService).scroll_all_tracks_volume)

        # Session2ARrangement encoder
        self.add_encoder(identifier=16, name="bounce session to arrangement",
                         on_press=self._container.get(SessionToArrangementService).bounce_session_to_arrangement)
