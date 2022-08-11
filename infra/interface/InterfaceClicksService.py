from protocol0.domain.shared.InterfaceClicksServiceInterface import InterfaceClicksServiceInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.infra.interface.PixelEnum import PixelEnum


class InterfaceClicksService(InterfaceClicksServiceInterface):
    def save_sample(self):
        # type: () -> None
        Backend.client().click_vertical_zone(*PixelEnum.SAVE_SAMPLE.coordinates)
