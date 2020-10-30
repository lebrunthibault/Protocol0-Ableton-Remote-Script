import pytest

from ClyphX_Pro.clyphx_pro.user_actions.lom.Song import Song


def test_song_empty_next_ext(song_empty):
    # type: (Song) -> None
    with pytest.raises(Exception):
        song_empty.action_next(True)
