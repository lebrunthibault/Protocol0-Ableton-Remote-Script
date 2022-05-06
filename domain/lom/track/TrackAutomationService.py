from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.shared.SongFacade import SongFacade


class TrackAutomationService(object):
    def __init__(self, track_factory):
        # type: (TrackFactory) -> None
        self._track_factory = track_factory

    def show_automation(self):
        # type: () -> None
        selected_parameter = SongFacade.selected_parameter()
        if selected_parameter and SongFacade.selected_clip_slot().clip:
            SongFacade.selected_clip().automation.show_parameter_envelope(selected_parameter)
        else:
            self._track_factory.add_dummy_track()
