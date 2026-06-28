from samvnstock import __version__


def test_version_is_string() -> None:
    assert isinstance(__version__, str)
    assert __version__ == "0.4.0"
