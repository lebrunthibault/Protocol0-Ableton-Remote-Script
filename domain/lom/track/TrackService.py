from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song


class TrackService(object):
    def __init__(self):
        # type: () -> None
        super(TrackService, self).__init__()
        DomainEventBus.subscribe(SelectedTrackChangedEvent, self._on_selected_track_changed_event)

    def _on_selected_track_changed_event(self, _):
        # type: (SelectedTrackChangedEvent) -> None
        if Song.selected_track().is_foldable:
            ApplicationView.show_device()

    def go_to_group_track(self):
        # type: () -> None
        if Song.selected_track().group_track is not None:
            Song.selected_track().group_track.select()
            ApplicationView.focus_session()
