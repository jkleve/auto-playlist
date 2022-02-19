from api.spotify import get_track_id


def test_get_track_id_empty():
    assert get_track_id("") is None


def test_get_track_id_one():
    assert get_track_id("https://spotify.com/track/azAZ09") == "azAZ09"
