from streamcontrol import constants

day_baseline = ["brooder", "birdpole", "chicken"]
night_baseline = ["brooder"]


def test_day_values():
    assert constants.DAY_SOURCES == day_baseline
    assert constants.NIGHT_SOURCES == night_baseline
