import pytest


@pytest.fixture
def key_yaml(tmp_path):
    p = tmp_path / "provider-config.yaml"
    p.write_text("google:\n  - KEY1:CX1\n  - KEY2:CX2\n", encoding="utf-8")
    return str(p)


@pytest.fixture
def empty_yaml(tmp_path):
    p = tmp_path / "provider-config.yaml"
    p.write_text("google:\n", encoding="utf-8")
    return str(p)
