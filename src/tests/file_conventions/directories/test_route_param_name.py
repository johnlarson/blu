def test_matches_arbitrary_segment():
    """A dynamic segment directory matches any URL segment."""
    ...


def test_nested():
    """Works when nested in another dynamic segment directory."""
    ...


def test_nested_with_static_segment():
    """
    Works when nested in both static and dynamic segment directories.
    """
    ...


def test_multiple_dynamic_segments():
    """
    If there are two dynamic segment directories, and only one leads to
    a full match with the URL, that one will be used.
    """
    ...


def test_with_non_matching_static_segment():
    """
    Works when there is a non-matching static segment directory at the
    same level.
    """
    ...


def test_with_static_segment_with_no_full_match():
    """
    Works when at the same level as a static segment directory that
    doesn't lead to a full match with the URL being processed.
    """
    ...