from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.shared.Song import Song


class ActionGroupCut(ActionGroupInterface):
    CHANNEL = 8

    def configure(self):
        # type: () -> None
        # SPLiT encoder
        self.add_encoder(
            identifier=8,
            name="split scene",
            on_scroll=lambda: Song.selected_scene().crop_scroller.scroll,
            on_press=lambda: partial(
                self._container.get(SceneCrudComponent).split_scene, Song.selected_scene()
            ),
        )

        # CROP encoder
        self.add_encoder(
            identifier=12,
            name="crop scene",
            on_scroll=lambda: Song.selected_scene().crop_scroller.scroll,
            on_press=lambda: partial(
                self._container.get(SceneCrudComponent).crop_scene, Song.selected_scene()
            ),
        )

        # TAIL encoder
        self.add_encoder(
            identifier=14,
            name="isolate clip tail",
            on_press=lambda: Song.selected_track().isolate_clip_tail,
        )
