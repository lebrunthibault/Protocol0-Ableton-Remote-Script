from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.loop.Looper import Looper
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.shared.SongFacade import SongFacade


class ActionGroupSet(ActionGroupInterface):
    CHANNEL = 8

    def configure(self):
        # type: () -> None
        # STaRT encoder
        self.add_encoder(
            identifier=1,
            name="scroll clip start",
            on_scroll=lambda: Looper(SongFacade.current_loop()).scroll_start,
        )

        # END encoder
        self.add_encoder(
            identifier=2,
            name="scroll clip end",
            on_scroll=lambda: Looper(SongFacade.current_loop()).scroll_end,
        )

        # LOOP encoder
        self.add_encoder(
            identifier=3,
            name="scroll loop",
            on_scroll=lambda: Looper(SongFacade.current_loop()).scroll_loop,
        )

        # SPLiT encoder
        self.add_encoder(
            identifier=8,
            name="split scene",
            on_scroll=lambda: SongFacade.selected_scene().crop_scroller.scroll,
            on_press=lambda: partial(
                self._container.get(SceneCrudComponent).split_scene, SongFacade.selected_scene()
            ),
        )

        # CROP encoder
        self.add_encoder(
            identifier=12,
            name="crop scene",
            on_scroll=lambda: SongFacade.selected_scene().crop_scroller.scroll,
            on_press=lambda: partial(
                self._container.get(SceneCrudComponent).crop_scene, SongFacade.selected_scene()
            ),
        )

        # Session/ARrangement encoder
        self.add_encoder(
            identifier=13,
            name="toggle session / arrangement",
            on_press=ApplicationViewFacade.toggle_session_arrangement,
        )
