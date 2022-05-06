from protocol0.domain.lom.clip.ClipEnvelopeShowedEvent import ClipEnvelopeShowedEvent
from protocol0.domain.shared.InterfaceClicksServiceInterface import InterfaceClicksServiceInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.interface.PixelEnum import PixelEnum


class InterfaceClicksService(InterfaceClicksServiceInterface):
    # NB: for an unknown reason clip.view.show_envelope does not always show the envelope
    # when the button was not clicked. As a workaround we click it the first time
    CLIP_ENVELOPE_SHOW_BOX_CLICKED = False

    def __init__(self):
        # type: () -> None
        DomainEventBus.subscribe(ClipEnvelopeShowedEvent, self._on_clip_envelope_showed_event)

    def _on_clip_envelope_showed_event(self, _):
        # type: (ClipEnvelopeShowedEvent) -> None
        if InterfaceClicksService.CLIP_ENVELOPE_SHOW_BOX_CLICKED:
            Backend.client().double_click(*PixelEnum.SHOW_CLIP_ENVELOPE.coordinates)
        InterfaceClicksService.CLIP_ENVELOPE_SHOW_BOX_CLICKED = True

    def save_sample(self):
        # type: () -> None
        Backend.client().click_vertical_zone(*PixelEnum.SAVE_SAMPLE.coordinates)
