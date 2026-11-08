import pytest

from dorker.config import load_keys
from dorker.exceptions import ConfigError


async def test_load_keys(key_yaml):
    keys = await load_keys(key_yaml)
    assert len(keys) == 2
    assert keys[0].api_key == "KEY1"
    assert keys[0].cx_id == "CX1"


async def test_load_empty(empty_yaml):
    with pytest.raises(ConfigError):
        await load_keys(empty_yaml)


async def test_load_missing():
    with pytest.raises(ConfigError):
        await load_keys("/nonexistent/path.yaml")
