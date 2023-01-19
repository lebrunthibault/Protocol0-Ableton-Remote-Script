from protocol0.domain.lom.clip_slot.ClipSlotHasClipEvent import ClipSlotHasClipEvent
from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.ApplicationViewFacade import ApplicationViewFacade
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song


class TrackService(object):
    def __init__(self):
        # type: () -> None
        super(TrackService, self).__init__()
        DomainEventBus.subscribe(SelectedTrackChangedEvent, self._on_selected_track_changed_event)
        DomainEventBus.subscribe(ClipSlotHasClipEvent, self._on_clip_slot_has_clip_event)

    def _on_clip_slot_has_clip_event(self, event):
        # type: (ClipSlotHasClipEvent) -> None
        track = Song.live_track_to_simple_track(event.live_track)
        if isinstance(track, SimpleAudioTrack):
            track.data.save()

    def _on_selected_track_changed_event(self, _):
        # type: (SelectedTrackChangedEvent) -> None
        if Song.selected_track().is_foldable:
            ApplicationViewFacade.show_device()

    def go_to_group_track(self):
        # type: () -> None
        if Song.selected_track().group_track is not None:
            Song.selected_track().group_track.select()
            ApplicationViewFacade.focus_session()
