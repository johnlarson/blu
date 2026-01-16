def test_matching_segment():
    """Should match a segment that equals the directory name."""
    ...


def test_leading_underscore():
    """
    A directory with a leading underscore is not treated as a static
    segment.
    """
    ...


def test_trailing_underscore():
    """
    A directory with a trailing underscore is not treated as a static
    segment.
    """
    ...


def test_nested():
    """Nested directories are treated as sequential URL segments."""
    ...


def test_has_priority_over_dynamic_segment():
    """
    When both a static segment directory and a dynamic segment directory
    match a segment in a URL, the static segment will be matched.
    """
    ...