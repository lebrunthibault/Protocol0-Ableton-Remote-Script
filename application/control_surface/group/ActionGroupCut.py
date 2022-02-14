from protocol0.application.control_surface.ActionGroupMixin import ActionGroupMixin
from protocol0.shared.SongFacade import SongFacade


class ActionGroupSet(ActionGroupMixin):
    CHANNEL = 8

    def configure(self):
        # type: () -> None
        # STaRT encoder
        self.add_encoder(identifier=1,
                         name="clip start",
                         on_scroll=lambda: SongFacade.selected_midi_clip().loop.scroll_start,
                         )

        # END encoder
        self.add_encoder(identifier=2,
                         name="clip end",
                         on_scroll=lambda: SongFacade.selected_midi_clip().loop.scroll_end,
                         )

        # CUT encoder
        self.add_encoder(identifier=3,
                         name="copy and paste clip to new scene",
                         on_scroll=lambda: SongFacade.current_external_synth_track().loop.scroll_end,
                         )
