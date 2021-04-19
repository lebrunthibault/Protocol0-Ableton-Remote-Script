from typing import Any

from _Framework.SubjectSlot import subject_slot_group
from a_protocol_0.lom.clip.AudioClip import AudioClip
from a_protocol_0.lom.clip_slot.ClipSlot import ClipSlot
from a_protocol_0.lom.track.simple_track.SimpleAudioTrack import SimpleAudioTrack
from a_protocol_0.utils.decorators import defer


class AudioBusTrack(SimpleAudioTrack):
    """
    Corresponds to the audio bus track in my sets
    This is where is stored the base dummy clip that is copied over when
    generating automation dummy clips. It is thus mandatory.
    It should be BASE_DUMMY_CLIP_BAR_LENGTH bars long with empty audio.
    """

    CLIP_WARPING_MANDATORY = True
    BASE_DUMMY_CLIP_BAR_LENGTH = 32

    def __init__(self, *a, **k):
        # type: (Any, Any) -> None
        super(AudioBusTrack, self).__init__(*a, **k)

        assert self.is_audio, "AudioBusTrack should be audio"

        self.parent.defer(self._check_clip_structure)

    @property
    def base_dummy_clip(self):
        # type: () -> AudioClip
        assert isinstance(self.clip_slots[0].clip, AudioClip), "The base dummy clip does not exist"
        return self.clip_slots[0].clip

    @subject_slot_group("map_clip")
    @defer
    def _map_clip_listener(self, clip_slot):
        # type: (ClipSlot) -> None
        self._check_clip_structure()

    def _check_clip_structure(self):
        # type: () -> None
        assert self.base_dummy_clip, "The base dummy clip should be the first one"

        self.base_dummy_clip.warping = True
        self.base_dummy_clip.length = self.BASE_DUMMY_CLIP_BAR_LENGTH * self.song.signature_denominator

        # cleaning unnecessary clips usually created when duplicating scenes
        if len(self.clips) > 1:
            [clip.delete() for clip in self.clips[1:]]
