from dorker.recon.common import clean_results, normalize_target
from dorker.recon.filter import filter_urls


def test_target_normalization():
    assert normalize_target("https://Example.com/path") == "example.com"


def test_scope_and_deduplication():
    urls = [
        "https://example.com/a",
        "https://example.com/a",
        "https://sub.example.com/b",
        "https://outside.test/",
    ]
    assert clean_results(urls, "example.com") == ["https://example.com/a"]
    assert clean_results(urls, "example.com", include_subdomains=True) == [
        "https://example.com/a",
        "https://sub.example.com/b",
    ]


def test_regex_filter():
    assert filter_urls(
        ["https://x.test/admin", "https://x.test/home"], "admin|login"
    ) == ["https://x.test/admin"]
