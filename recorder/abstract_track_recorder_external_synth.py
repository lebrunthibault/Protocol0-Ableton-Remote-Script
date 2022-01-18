from functools import partial

from protocol0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.recorder.track_recorder_interface import TrackRecorderInterface
from protocol0.sequence.Sequence import Sequence


class AbstractTrackRecorderExternalSynth(TrackRecorderInterface):
    def __init__(self, track):
        # type: (ExternalSynthTrack) -> None
        super(AbstractTrackRecorderExternalSynth, self).__init__(track=track)
        self.track = track

    def record(self, bar_length):
        # type: (int) -> None
        seq = Sequence()

        record_step = [
            partial(self.track.midi_track.clip_slots[self.next_empty_clip_slot_index].record, bar_length=bar_length),
            partial(self.track.audio_track.clip_slots[self.next_empty_clip_slot_index].record, bar_length=bar_length),
        ]

        if self.track.record_clip_tails:
            audio_tail_clip_slot = self.track.audio_tail_track.clip_slots[self.next_empty_clip_slot_index]
            record_step.append(partial(audio_tail_clip_slot.record, bar_length=bar_length))

        seq.add(record_step)
        seq.add(self.song.selected_scene.fire)

    def post_record(self):
        # type: () -> None
        self.track.instrument.activate_editor_automation()
        self.system.hide_plugins()
        # this is delayed in the case an encoder is touched after the recording is finished by mistake
        self.parent.wait([1, 10, 100], self.song.re_enable_automation)

        midi_clip = self.track.midi_track.playable_clip
        audio_clip = self.track.audio_track.playable_clip
        if not midi_clip or not audio_clip:
            return None

        audio_clip.clip_name.update(base_name=midi_clip.clip_name.base_name)

        midi_clip.select()
        midi_clip.show_loop()
        self.parent.navigationManager.focus_main()
