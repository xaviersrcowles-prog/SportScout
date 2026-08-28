from app.utils.geo import bounding_box, haversine_distance_miles, in_bounding_box


def test_haversine_zero_distance():
    assert haversine_distance_miles(42.36, -71.06, 42.36, -71.06) == 0.0


def test_haversine_known_distance():
    # Boston to Cambridge is roughly 2.5-3 miles apart.
    distance = haversine_distance_miles(42.3601, -71.0589, 42.3736, -71.1097)
    assert 2.0 < distance < 4.0


def test_bounding_box_contains_center():
    box = bounding_box(42.36, -71.06, 5)
    assert in_bounding_box(42.36, -71.06, box)


def test_bounding_box_excludes_far_point():
    box = bounding_box(42.36, -71.06, 5)
    assert not in_bounding_box(45.0, -71.06, box)
