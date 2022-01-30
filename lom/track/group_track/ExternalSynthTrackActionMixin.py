from functools import partial

from typing import TYPE_CHECKING, Optional

from protocol0.components.TrackDataManager import save_track_data
from protocol0.errors.Protocol0Warning import Protocol0Warning
from protocol0.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


# noinspection PyTypeHints
class ExternalSynthTrackActionMixin(object):
    def arm_track(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        self.base_track.is_folded = False
        self.base_track.mute = False

        if self.song.usamo_track:
            self.song.usamo_track.input_routing_track = self.midi_track

        self.monitoring_state.monitor_midi()

        seq = Sequence()
        seq.add([sub_track.arm for sub_track in self.sub_tracks if not isinstance(sub_track, SimpleDummyTrack)])
        return seq.done()

    def unarm_track(self):
        # type: (ExternalSynthTrack) -> None
        self.monitoring_state.monitor_audio()

    @save_track_data
    def toggle_record_clip_tails(self):
        # type: (ExternalSynthTrack) -> None
        if self.audio_tail_track is None:
            raise Protocol0Warning("Please create a clip tail track")

        self.record_clip_tails = not self.record_clip_tails
        self.parent.show_message("Record clip tails %s" % "ON" if self.record_clip_tails else "OFF")

    def scroll_presets_or_samples(self, go_next):
        # type: (ExternalSynthTrack, bool) -> Sequence
        """ overridden """
        seq = Sequence()
        if not self.can_change_presets:
            seq.add(self._disable_protected_mode)

        seq.add(partial(super(ExternalSynthTrackActionMixin, self).scroll_presets_or_samples, go_next=go_next))
        return seq.done()

    @property
    def can_change_presets(self):
        # type: (ExternalSynthTrack) -> bool
        return len(self.audio_track.clips) == 0 or \
               not self.protected_mode_active or \
               not self.instrument.HAS_PROTECTED_MODE

    def _disable_protected_mode(self):
        # type: (ExternalSynthTrack) -> Sequence
        seq = Sequence()
        seq.prompt("Disable protected mode ?")
        seq.add(partial(setattr, self, "protected_mode_active", False))
        seq.add(partial(self.parent.show_message, "track protected mode disabled"))
        return seq.done()
