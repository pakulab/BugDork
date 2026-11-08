from dorker.core.dorker import Dorker
from dorker.core.keypool import KeyPool
from dorker.models import Key, RunConfig


class FakeClient:
    def __init__(self, pages):
        self.pages = pages
        self.calls = 0

    async def search(self, key, dork, start):
        page = self.pages[self.calls]
        self.calls += 1
        return page, False


async def test_pagination():
    page1 = [f"https://a{i}" for i in range(10)]
    page2 = [f"https://b{i}" for i in range(5)]

    fake = FakeClient([page1, page2])
    cfg = RunConfig(threads=1, max_results=100, delay=0)
    dorker = Dorker(fake, KeyPool([Key("k", "cx")]), cfg)
    results = await dorker.run(["dork1"])

    assert len(results[0].urls) == 15
    assert results[0].urls == sorted(page1 + page2)


async def test_pagination_stops_at_cap():
    page1 = [f"https://a{i}" for i in range(10)]
    page2 = [f"https://b{i}" for i in range(10)]

    fake = FakeClient([page1, page2])
    cfg = RunConfig(threads=1, max_results=15, delay=0)
    dorker = Dorker(fake, KeyPool([Key("k", "cx")]), cfg)
    results = await dorker.run(["dork1"])

    assert len(results[0].urls) == 15


async def test_pagination_stops_on_empty():
    page1 = [f"https://a{i}" for i in range(10)]

    fake = FakeClient([page1, []])
    cfg = RunConfig(threads=1, max_results=100, delay=0)
    dorker = Dorker(fake, KeyPool([Key("k", "cx")]), cfg)
    results = await dorker.run(["dork1"])

    assert len(results[0].urls) == 10
