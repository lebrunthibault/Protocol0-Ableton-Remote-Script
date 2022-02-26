from protocol0.domain.lom.clip.ClipEnveloppeShowedEvent import ClipEnveloppeShowedEvent
from protocol0.domain.shared.DomainEventBus import DomainEventBus
from protocol0.domain.shared.InterfaceClicksServiceInterface import InterfaceClicksServiceInterface
from protocol0.domain.shared.backend.System import System
from protocol0.infra.interface.PixelEnum import PixelEnum


class InterfaceClicksService(InterfaceClicksServiceInterface):
    # NB: for an unknown reason clip.view.show_envelope does not always show the envelope
    # when the button was not clicked. As a workaround we click it the first time
    CLIP_ENVELOPE_SHOW_BOX_CLICKED = False

    def __init__(self):
        # type: () -> None
        DomainEventBus.subscribe(ClipEnveloppeShowedEvent, self._on_clip_enveloppe_showed_event)

    def _on_clip_enveloppe_showed_event(self, _):
        # type: (ClipEnveloppeShowedEvent) -> None
        if InterfaceClicksService.CLIP_ENVELOPE_SHOW_BOX_CLICKED:
            System.client().double_click(*PixelEnum.SHOW_CLIP_ENVELOPE.coordinates)
        InterfaceClicksService.CLIP_ENVELOPE_SHOW_BOX_CLICKED = True

    def save_sample(self):
        # type: () -> None
        System.client().click_vertical_zone(*PixelEnum.SAVE_SAMPLE.coordinates)
