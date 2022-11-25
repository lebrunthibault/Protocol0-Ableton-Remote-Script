from functools import partial

from protocol0.application.ScriptResetActivatedEvent import ScriptResetActivatedEvent
from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.set.SessionToArrangementService import SessionToArrangementService
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.SongFacade import SongFacade


class ActionGroupSet(ActionGroupInterface):
    CHANNEL = 3

    def configure(self):
        # type: () -> None
        # midi clip to MONO encoder
        self.add_encoder(
            identifier=4,
            name="midi clip to mono",
            on_press=lambda: SongFacade.selected_clip(MidiClip).to_mono,
        )

        # INIT song encoder
        # when something (e.g. scene mapping goes haywire, rebuild mappings)
        self.add_encoder(
            identifier=13,
            name="(re) initialize the script",
            on_press=partial(DomainEventBus.emit, ScriptResetActivatedEvent()),
        )

        # Session2ARrangement encoder
        self.add_encoder(
            identifier=16,
            name="bounce session to arrangement",
            on_press=self._container.get(SessionToArrangementService).bounce_session_to_arrangement,
        )
