from a_protocol_0.lom.clip.AudioClip import AudioClip
from a_protocol_0.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleAudioTrack(SimpleTrack):
    CLIP_CLASS = AudioClip
    CLIP_WARPING_MANDATORY = False
