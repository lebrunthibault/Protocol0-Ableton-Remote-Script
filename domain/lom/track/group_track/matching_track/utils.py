from functools import partial

from typing import TYPE_CHECKING, Optional, List

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


def assert_valid_track_name(track_name):
    # type: (str) -> None
    from protocol0.domain.lom.device.DeviceEnum import DeviceEnum

    excluded_names = [d.value.lower() for d in DeviceEnum if d.is_instrument]
    excluded_names += ["synth"]

    assert track_name.lower() not in excluded_names, "Track name should be specific"


def ensure_clips_looped(clips):
    # type: (List[Clip]) -> None
    unlooped_clips = [clip for clip in clips if not clip.looping]
    if len(unlooped_clips) > 0:
        Logger.info("Looping unlooped clips")

    for clip in unlooped_clips:
        clip.looping = True


def is_valid_matching_track(track, audio_track):
    # type: (SimpleTrack, SimpleTrack) -> bool
    from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack

    return (
        not isinstance(track, NormalGroupTrack)
        and track != audio_track
        and liveobj_valid(track._track)
        and track.name == audio_track.name
    )


def get_matching_audio_track(base_track):
    # type: (AbstractTrack) -> Optional[SimpleAudioTrack]
    from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

    # restrict the search
    audio_tracks = [
        t
        for t in Song.simple_tracks(SimpleAudioTrack)
        if base_track.index + 5 > t.index > base_track.index
        and t.group_track == base_track.group_track
    ]
    return find_if(partial(is_valid_matching_track, base_track), audio_tracks)
