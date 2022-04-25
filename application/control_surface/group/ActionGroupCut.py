from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.loop.Looper import Looper
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.shared.SongFacade import SongFacade


class ActionGroupSet(ActionGroupInterface):
    CHANNEL = 8

    def configure(self):
        # type: () -> None
        # STaRT encoder
        self.add_encoder(identifier=1,
                         name="scroll clip start",
                         on_scroll=lambda: Looper(SongFacade.current_loop()).scroll_start,
                         )

        # END encoder
        self.add_encoder(identifier=2,
                         name="scroll clip end",
                         on_scroll=lambda: Looper(SongFacade.current_loop()).scroll_end,
                         )

        # LOOP encoder
        self.add_encoder(identifier=3,
                         name="scroll loop",
                         on_scroll=lambda: Looper(SongFacade.current_loop()).scroll_loop,
                         )

        # CUT encoder
        self.add_encoder(identifier=4,
                         name="copy and paste clip to new scene",
                         on_press=lambda: SongFacade.current_external_synth_track().copy_and_paste_clips_to_new_scene,
                         )

        # SPLiT encoder
        self.add_encoder(identifier=8,
                         name="split scene",
                         on_scroll=lambda: SongFacade.selected_scene().crop_scroller.scroll,
                         on_press=lambda: SongFacade.selected_scene().split
                         )

        # CROP encoder
        self.add_encoder(identifier=12,
                         name="crop scene",
                         on_scroll=lambda: SongFacade.selected_scene().crop_scroller.scroll,
                         on_press=lambda: partial(SongFacade.selected_scene().crop)
                         )

        # Session/ARrangement encoder
        self.add_encoder(identifier=13,
                         name="toggle session / arrangement",
                         on_press=ApplicationViewFacade.toggle_session_arrangement
                         )
