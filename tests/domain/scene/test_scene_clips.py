from typing import cast

from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.shared.Song import Song
from protocol0.tests.domain.fixtures.clip_slot import AbletonClipSlot
from protocol0.tests.domain.fixtures.p0 import make_protocol0


def test_scene_clips():
    make_protocol0()
    clips = SceneClips(0)
    assert len(list(clips)) == 0
    clip_slot = Song.selected_track().clip_slots[0]
    cast(AbletonClipSlot, clip_slot._clip_slot).add_clip()
    clip_slot._has_clip_listener()

    clips = SceneClips(0)
    assert len(list(clips)) == 1
