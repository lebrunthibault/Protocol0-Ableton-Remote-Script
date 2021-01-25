import itertools

from _Framework.SubjectSlot import subject_slot
from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack


class AutomationTracksCouple(AbstractObject):
    """ helper class to simplify operations on automation tracks. The linking of clip_slots and clips is done here """
    def __init__(self, audio_track, midi_track, *a, **k):
        # type: (AutomationAudioTrack, AutomationMidiTrack) -> None
        super(AutomationTracksCouple, self).__init__(*a, **k)

        if audio_track.index != midi_track.index - 1:
            raise Protocol0Error("Inconsistent automation track state, midi should always be right adjacent to audio")

        self.audio_track = audio_track
        self.midi_track = midi_track
        self._connect.subject = self.midi_track

        self.parent.defer(self._connect)

    @subject_slot("clip_slots")
    def _connect(self):
        self.audio_track._get_automated_device_and_parameter()
        self.midi_track._connect(self.audio_track)

        for audio_clip_slot, midi_clip_slot in itertools.izip(self.audio_track.clip_slots, self.midi_track.clip_slots):
            midi_clip_slot._connect(audio_clip_slot)
            if midi_clip_slot.has_clip:
                midi_clip_slot.clip._connect(audio_clip_slot.clip)

