from typing import cast

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.shared.SongFacade import SongFacade
from protocol0.tests.domain.fixtures.clip import AbletonClip
from protocol0.tests.domain.fixtures.clip_slot import AbletonClipSlot
from protocol0.tests.domain.fixtures.p0 import make_protocol0


def test_scene_length():
    make_protocol0()
    clips = SceneClips(0)
    scene_length = SceneLength(clips)
    assert scene_length.length == 0
    assert scene_length.bar_length == 0

    clip_slot = SongFacade.selected_track().clip_slots[0]
    live_clip_slot = cast(AbletonClipSlot, clip_slot._clip_slot)
    live_clip_slot.add_clip()
    live_clip_slot.clip.length = 4

    live_clip = AbletonClip()
    live_clip.length = 4
    clips._clips.append(Clip.make(clip_slot))
    assert scene_length.length == 4
    assert scene_length.bar_length == 1
