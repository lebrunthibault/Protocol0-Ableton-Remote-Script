from typing import cast

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipConfig import ClipConfig
from protocol0.shared.Song import Song
from protocol0.tests.domain.fixtures.clip_slot import AbletonClipSlot
from protocol0.tests.domain.fixtures.p0 import make_protocol0


def test_clip_playing_position():
    make_protocol0()
    clip_slot = Song.selected_track().clip_slots[0]
    live_clip_slot = cast(AbletonClipSlot, clip_slot._clip_slot)
    live_clip_slot.add_clip()
    live_clip_slot.clip.length = 4
    clip = Clip(live_clip_slot.clip, 1, ClipConfig(1))
    assert clip.playing_position.position == 0

    live_clip_slot.clip.length = 16
    live_clip_slot.clip.playing_position = 5.0
    clip = Clip(live_clip_slot.clip, 2, ClipConfig(2))
    assert clip.playing_position.position == 5
