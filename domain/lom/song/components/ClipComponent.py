import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Optional

from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipSlotSelectedEvent import ClipSlotSelectedEvent
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Config import Config
from protocol0.shared.Song import Song


class ClipComponent(SlotManager):
    def __init__(self, song_view):
        # type: (Live.Song.Song.View) -> None
        super(ClipComponent, self).__init__()
        self._view = song_view

        self._detail_clip_listener.subject = self._view

        DomainEventBus.subscribe(ClipSlotSelectedEvent, self.on_clip_slot_selected_event)
        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: self.disconnect())

    # CLIP SLOTS

    @subject_slot("detail_clip")
    def _detail_clip_listener(self):
        # type: () -> None
        if not Config.EXPERIMENTAL_FEATURES:
            return

        try:
            detail_clip = Song.selected_clip(MidiClip)
        except Protocol0Error:
            return

        detail_clip.show_notes()

    def on_clip_slot_selected_event(self, event):
        # type: (ClipSlotSelectedEvent) -> None
        # we need all tracks un folded for this
        ApplicationView.show_clip()

        # workaround to refocus the selected clip slot
        if event.live_clip_slot == self._view.highlighted_clip_slot:
            other_track = find_if(lambda t: t != Song.selected_track(), Song.simple_tracks())
            if other_track is None:
                return
            self._view.highlighted_clip_slot = other_track.clip_slots[0]._clip_slot

        self._view.highlighted_clip_slot = event.live_clip_slot

    # CLIPS

    @property
    def selected_clip(self):
        # type: () -> Optional[Clip]
        return Song.selected_clip()

    @property
    def draw_mode(self):
        # type: () -> bool
        return self._view.draw_mode

    @draw_mode.setter
    def draw_mode(self, draw_mode):
        # type: (bool) -> None
        self._view.draw_mode = draw_mode
