from a_protocol_0.errors.Protocol0Error import Protocol0Error
from a_protocol_0.lom.AbstractObject import AbstractObject
from a_protocol_0.lom.ObjectSynchronizer import ObjectSynchronizer
from a_protocol_0.lom.track.simple_track.AutomationAudioTrack import AutomationAudioTrack
from a_protocol_0.lom.track.simple_track.AutomationMidiTrack import AutomationMidiTrack
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class AutomationTracksCouple(AbstractObject):
    """ helper class to simplify operations on automation tracks. The linking of clip_slots and clips is done here """
    def __init__(self, group_track, audio_simple_track, midi_simple_track, *a, **k):
        # type: (SimpleTrack, SimpleTrack, SimpleTrack) -> None
        super(AutomationTracksCouple, self).__init__(*a, **k)

        if audio_simple_track.index != midi_simple_track.index - 1:
            raise Protocol0Error("Inconsistent automation track state, midi should always be right adjacent to audio, \n audio: %s, \n midi: %s" % (audio_simple_track, midi_simple_track))

        self.audio_track = AutomationAudioTrack(audio_simple_track._track, audio_simple_track.index)
        self.midi_track = AutomationMidiTrack(midi_simple_track._track, midi_simple_track.index)
        self.midi_track.linked_track = self.audio_track
        self.audio_track.linked_track = self.audio_track

        self._track_synchronizer = ObjectSynchronizer(self.audio_track, self.midi_track, "_track", ["mute", "solo"])
        self.audio_track._set_automated_device_and_parameter()

        # replace obsolete simple_tracks
        self.song.simple_tracks[audio_simple_track.index] = self.audio_track
        self.song.simple_tracks[midi_simple_track.index] = self.midi_track

        self.parent.songManager._live_track_to_simple_track[audio_simple_track._track] = self.audio_track
        self.parent.songManager._live_track_to_simple_track[midi_simple_track._track] = self.midi_track

        group_track.sub_tracks[group_track.sub_tracks.index(audio_simple_track)] = self.audio_track
        group_track.sub_tracks[group_track.sub_tracks.index(midi_simple_track)] = self.midi_track
        group_track.sub_tracks.pop()  # removing the tracks that are automatically added to the list
        group_track.sub_tracks.pop()

        audio_simple_track.disconnect()
        midi_simple_track.disconnect()

    def disconnect(self):
        super(AutomationTracksCouple, self).disconnect()
        self._track_synchronizer.disconnect()

