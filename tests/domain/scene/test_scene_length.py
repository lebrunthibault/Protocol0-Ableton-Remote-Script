from typing import cast

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipConfig import ClipConfig
from protocol0.domain.lom.scene.SceneClips import SceneClips, SceneClipSlot
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.shared.Song import Song
from protocol0.tests.domain.fixtures.clip import AbletonClip
from protocol0.tests.domain.fixtures.clip_slot import AbletonClipSlot
from protocol0.tests.domain.fixtures.p0 import make_protocol0


def test_scene_length():
    make_protocol0()
    clips = SceneClips(0)
    scene_length = SceneLength(clips, 0)
    assert scene_length.length == 0
    assert scene_length.bar_length == 0

    clip_slot = Song.selected_track().clip_slots[0]
    live_clip_slot = cast(AbletonClipSlot, clip_slot._clip_slot)
    live_clip_slot.add_clip()
    live_clip_slot.clip.length = 4

    live_clip = AbletonClip()
    live_clip.length = 4
    clip_slot = AbletonClipSlot()
    clip_slot.has_clip = True
    clip_slot.clip = Clip(live_clip_slot.clip, 1, ClipConfig(1))
    clips._clip_slot_tracks.append(SceneClipSlot(None, clip_slot))  # noqa

    assert scene_length.length == 4
    assert scene_length.bar_length == 1
