from typing import cast

from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.domain.lom.scene.ScenePlayingState import ScenePlayingState
from protocol0.shared.Song import Song
from protocol0.tests.domain.fixtures.clip_slot import AbletonClipSlot
from protocol0.tests.domain.fixtures.p0 import make_protocol0


def test_scene_playing_state():
    make_protocol0()
    clip_slot = Song.selected_track().clip_slots[0]
    live_clip_slot = cast(AbletonClipSlot, clip_slot._clip_slot)
    live_clip_slot.add_clip()
    live_clip_slot.clip.length = 8
    live_clip_slot.clip.is_playing = True
    clip_slot._has_clip_listener()
    clips = SceneClips(0)

    scene_length = SceneLength(clips, 0)
    scene_position = ScenePlayingState(clips, scene_length)
    assert scene_position.position == 0
    assert scene_position.bar_position == 0
    assert scene_position.current_bar == 0

    live_clip_slot.clip.playing_position = 2.0
    assert scene_position.position == 2
    assert scene_position.bar_position == 0.5
    assert scene_position.current_bar == 0

    live_clip_slot.clip.playing_position = 4.0
    assert scene_position.position == 4
    assert scene_position.bar_position == 1
    assert scene_position.current_bar == 1
