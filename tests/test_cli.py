import pytest

from dorker.cli import parse_args


def test_defaults():
    cfg = parse_args([])
    assert cfg.threads == 20
    assert cfg.fmt == "txt"
    assert cfg.max_results == 100


def test_invalid_threads():
    with pytest.raises(SystemExit):
        parse_args(["-t", "0"])


def test_invalid_max_results():
    with pytest.raises(SystemExit):
        parse_args(["--max-results", "200"])
