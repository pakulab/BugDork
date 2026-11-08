import httpx
import respx

from dorker.core.client import CSE_URL, CSEClient
from dorker.models import Key


@respx.mock
async def test_success():
    respx.get(CSE_URL).mock(
        return_value=httpx.Response(
            200,
            json={"items": [{"link": "https://a"}, {"link": "https://b"}]},
        )
    )
    async with httpx.AsyncClient() as c:
        client = CSEClient(c, timeout=5, retries=1, delay=0)
        urls, exhausted = await client.search(Key("k", "cx"), "dork", 1)
    assert urls == ["https://a", "https://b"]
    assert exhausted is False


@respx.mock
async def test_quota():
    respx.get(CSE_URL).mock(
        return_value=httpx.Response(
            403,
            json={"error": {"errors": [{"reason": "quotaExceeded"}]}},
        )
    )
    async with httpx.AsyncClient() as c:
        client = CSEClient(c, timeout=5, retries=1, delay=0)
        urls, exhausted = await client.search(Key("k", "cx"), "dork", 1)
    assert urls == []
    assert exhausted is True
