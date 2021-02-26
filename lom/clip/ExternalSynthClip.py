from typing import TYPE_CHECKING

from a_protocol_0.lom.clip.Clip import Clip
from a_protocol_0.utils.decorators import p0_subject_slot

if TYPE_CHECKING:
    # noinspection PyUnresolvedReferences
    from a_protocol_0.lom.track.group_track.ExternalSynthTrack import ExternalSynthTrack


class ExternalSynthClip(Clip):
    def __init__(self, *a, **k):
        super(ExternalSynthClip, self).__init__(*a, **k)
        # handled in clip synchronizer now
        # self._name_listener.subject = self._clip
        # self._previous_name = self._clip.name
        # self._external_synth_track = self.track.abstract_group_track  # type: ExternalSynthTrack

    # @p0_subject_slot("name")
    # def _name_listener(self):
    #     """ linking clip names """
    #     other_clips = [clip for clip in self._external_synth_track.audio_track.clips + self._external_synth_track.midi_track.clips if clip != self]
    #     [setattr(clip, "name", self.name) for clip in other_clips if clip.name == self._previous_name]
    #     self._previous_name = self._clip.name
