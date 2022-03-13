from functools import partial

from typing import TYPE_CHECKING, Optional

from protocol0.domain.lom.track.simple_track.SimpleDummyTrack import SimpleDummyTrack
from protocol0.shared.SongFacade import SongFacade
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


# noinspection PyTypeHints
class ExternalSynthTrackActionMixin(object):
    def arm_track(self):
        # type: (ExternalSynthTrack) -> Optional[Sequence]
        self.base_track.is_folded = False
        self.base_track.muted = False

        if SongFacade.usamo_track():
            SongFacade.usamo_track().input_routing.track = self.midi_track
            SongFacade.usamo_device().device_on = True  # this is the default: overridden by prophet

        self.monitoring_state.monitor_midi()

        seq = Sequence()
        seq.add([sub_track.arm_track for sub_track in self.sub_tracks if not isinstance(sub_track, SimpleDummyTrack)])
        return seq.done()

    def unarm(self):
        # type: (ExternalSynthTrack) -> None
        super(ExternalSynthTrackActionMixin, self).unarm()
        self.monitoring_state.monitor_audio()

    @property
    def can_change_presets(self):
        # type: (ExternalSynthTrack) -> bool
        return len(self.audio_track.clips) == 0 or \
               not self.protected_mode_active or \
               not self.instrument.HAS_PROTECTED_MODE

    def disable_protected_mode(self):
        # type: (ExternalSynthTrack) -> Sequence
        seq = Sequence()
        seq.prompt("Disable protected mode ?")
        seq.add(partial(setattr, self, "protected_mode_active", False))
        seq.add(partial(StatusBar.show_message, "track protected mode disabled"))
        return seq.done()

    def copy_and_paste_clips_to_new_scene(self):
        # type: (ExternalSynthTrack) -> Sequence
        seq = Sequence()
        seq.add(SongFacade.selected_scene().duplicate)
        # seq.add(self.midi_track.clip_slots[SongFacade.selected_scene().index].clip.select)
        # seq.add(SongFacade.selected_scene().fire)
        seq.add(lambda: SongFacade.current_external_synth_track().midi_track.clip_slots[SongFacade.selected_scene().index].clip.crop())
        seq.add(lambda: SongFacade.current_external_synth_track().audio_track.clip_slots[SongFacade.selected_scene().index].clip.crop())
        seq.add()
        return seq.done()
