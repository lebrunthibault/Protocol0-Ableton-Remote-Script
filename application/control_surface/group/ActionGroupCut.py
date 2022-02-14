from functools import partial

from protocol0.application.control_surface.ActionGroupMixin import ActionGroupMixin
from protocol0.shared.SongFacade import SongFacade


class ActionGroupSet(ActionGroupMixin):
    CHANNEL = 8

    def configure(self):
        # type: () -> None
        # STaRT encoder
        self.add_encoder(identifier=1,
                         name="scroll clip start",
                         on_scroll=lambda: SongFacade.selected_midi_clip().loop.scroll_start,
                         )

        # END encoder
        self.add_encoder(identifier=2,
                         name="scroll clip end",
                         on_scroll=lambda: SongFacade.selected_midi_clip().loop.scroll_end,
                         )

        # LOOP encoder
        self.add_encoder(identifier=3,
                         name="scroll loop",
                         on_scroll=lambda: SongFacade.selected_midi_clip().loop.scroll_loop,
                         )

        # CUT encoder
        self.add_encoder(identifier=4,
                         name="copy and paste clip to new scene",
                         on_press=lambda: SongFacade.current_external_synth_track().copy_and_paste_clips_to_new_scene,
                         )

        # 2 bars loop encoder
        self.add_encoder(identifier=13,
                         name="2 bars loop",
                         on_press=lambda: partial(SongFacade.selected_midi_clip().loop.set_loop_bar_length, 2),
                         )

        # 4 bars loop encoder
        self.add_encoder(identifier=14,
                         name="4 bars loop",
                         on_press=lambda: partial(SongFacade.selected_midi_clip().loop.set_loop_bar_length, 4),
                         )

        # 8 bars loop encoder
        self.add_encoder(identifier=15,
                         name="8 bars loop",
                         on_press=lambda: partial(SongFacade.selected_midi_clip().loop.set_loop_bar_length, 8),
                         )

        # 16 bars loop encoder
        self.add_encoder(identifier=16,
                         name="16 bars loop",
                         on_press=lambda: partial(SongFacade.selected_midi_clip().loop.set_loop_bar_length, 16),
                         )
