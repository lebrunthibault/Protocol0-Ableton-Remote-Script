import pytest

def test_song_empty_next_ext(song_empty):
    with pytest.raises(Exception):
        song_empty.action_next(True)
