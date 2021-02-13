import time
from functools import partial
import Live

from typing import TYPE_CHECKING

from a_protocol_0.devices.InstrumentMinitaur import InstrumentMinitaur
from a_protocol_0.lom.Colors import Colors
from a_protocol_0.sequence.Sequence import Sequence

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


# noinspection PyTypeHints
class ExternalSynthTrackActionMixin(object):
    def action_arm_track(self):
        # type: (ExternalSynthTrack) -> None
        self.color = Colors.ARM
        self.base_track.is_folded = False
        self.midi.action_arm_track()
        self.audio.action_arm_track()
        self.midi.has_monitor_in = False
        self.audio.has_monitor_in = True

    def action_unarm_track(self):
        # type: (ExternalSynthTrack) -> None
        self.midi.has_monitor_in = self.audio.has_monitor_in = False
        if isinstance(self.instrument, InstrumentMinitaur):
            self.midi.has_monitor_in = True  # needed when we have multiple minitaur tracks so that other midi clips are not sent to minitaur

    def action_switch_monitoring(self):
        # type: (ExternalSynthTrack) -> None
        if self.midi.has_monitor_in and self.audio.has_monitor_in:
            self.midi.has_monitor_in = self.audio.has_monitor_in = False
        elif self.audio.has_monitor_in:
            self.midi.has_monitor_in = True
        else:
            self.audio.has_monitor_in = True

    def action_record_all(self):
        # type: (ExternalSynthTrack) -> None
        seq = Sequence()
        seq.add([
            partial(self.midi.action_record_all, clip_slot_index=self.next_empty_clip_slot_index),
            partial(self.audio.action_record_all, clip_slot_index=self.next_empty_clip_slot_index)
        ])
        return seq.done()

    def action_record_audio_only(self, overwrite=False):
        # type: (ExternalSynthTrack, bool) -> None
        clip_slot_index = self.midi.playable_clip.index if not self.audio.clip_slots[
            self.midi.playable_clip.index].has_clip else None
        self.midi.playable_clip.start_marker = 0
        self.song.recording_bar_count = int(round((self.midi.playable_clip.length + 1) / 4))

        seq = Sequence()
        if overwrite:
            last_linked_clip = next(
                reversed([clip for clip in self.audio.clips if clip.name == self.midi.playable_clip.name]), None)
            if last_linked_clip:
                clip_slot_index = last_linked_clip.index
                seq.add(last_linked_clip.delete, wait=2)

        seq.add(lambda: setattr(self.midi.playable_clip, "is_playing", True))
        seq.add(partial(self.audio.action_record_all, clip_slot_index=clip_slot_index))
        return seq.done()

    def action_undo_track(self):
        # type: (ExternalSynthTrack) -> None
        [sub_track.action_undo_track() for sub_track in self.sub_tracks]

    def _post_record(self, only_audio):
        # type: (ExternalSynthTrack, bool) -> None
        self.song.metronome = False
        self.midi.has_monitor_in = False
        self.audio.has_monitor_in = True
        self._rename_recorded_clips(only_audio=only_audio)
        self.audio.playable_clip.warp_mode = Live.Clip.WarpMode.complex_pro
        seq = Sequence()
        seq.add(partial(self.song.select_track, self.audio), wait=2)
        seq.add(lambda: setattr(self.song, "highlighted_clip_slot", self.audio.playable_clip.clip_slot))
        seq.add(self.parent.clyphxNavigationManager.show_clip_view)
        seq.add(self.audio.playable_clip.quantize)
        return seq.done()

    def _rename_recorded_clips(self, only_audio):
        # type: (ExternalSynthTrack, bool) -> None
        if only_audio:
            self.audio.playable_clip.name = self.midi.playable_clip.name
        else:
            clip_name = str(int(time.time()))
            self.midi.playable_clip.name = clip_name
            self.audio.playable_clip.name = clip_name
