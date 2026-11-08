from dorker.core.keypool import KeyPool
from dorker.models import Key


async def test_round_robin():
    pool = KeyPool([Key("a", "1"), Key("b", "2")])
    seen = set()
    for _ in range(4):
        k = await pool.acquire()
        seen.add(k.api_key)
    assert seen == {"a", "b"}


async def test_exhaust():
    pool = KeyPool([Key("a", "1"), Key("b", "2")])
    k = await pool.acquire()
    await pool.exhaust(k)
    nxt = await pool.acquire()
    assert nxt.api_key != k.api_key
    await pool.exhaust(nxt)
    assert await pool.acquire() is None
    assert not pool
