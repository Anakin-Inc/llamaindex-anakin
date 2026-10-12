import logging
from typing import Any
from unittest.mock import create_autospec

import pytest
from anakin import Anakin
from anakin.errors import JobFailedError
from anakin.models import BatchScrapeResult, CrawlResult, Document, MapResult, SearchResult
from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import MetadataMode

from llama_index.readers.anakin import AnakinWebReader


def make_reader(mode: str = "scrape", **params: Any) -> tuple[AnakinWebReader, Any]:
    # Autospec a real client, so a call that doesn't match the SDK's signature fails.
    client = create_autospec(Anakin(api_key="ask_test"))
    reader = AnakinWebReader(api_key="ask_test", mode=mode, params=params, client=client)  # type: ignore[arg-type]
    return reader, client


def page(url: str, markdown: str = "content", job_id: str = "job_1") -> Document:
    return Document.model_validate(
        {"id": job_id, "url": url, "status": "completed", "markdown": markdown}
    )


def test_is_a_llamaindex_reader() -> None:
    assert issubclass(AnakinWebReader, BaseReader)
    assert AnakinWebReader.class_name() == "AnakinWebReader"


def test_api_key_is_not_serialized() -> None:
    reader, _ = make_reader()
    assert "api_key" not in reader.model_dump()
    assert "ask_test" not in reader.model_dump_json()


def test_scrape_one_url_passes_params_and_keys_the_document_by_url() -> None:
    reader, client = make_reader("scrape", use_browser=True, force_fresh=True)
    client.scrape.return_value = page("https://a.com/", "# A")

    (doc,) = reader.load_data(url="https://a.com")

    assert doc.text == "# A"
    assert doc.id_ == "https://a.com/"
    assert doc.metadata == {
        "source": "anakin",
        "mode": "scrape",
        "url": "https://a.com/",
        "job_id": "job_1",
        "cached": False,
    }
    client.scrape.assert_called_once_with("https://a.com", use_browser=True, force_fresh=True)


def test_bookkeeping_metadata_stays_out_of_embeddings_and_prompts() -> None:
    reader, client = make_reader("scrape")
    client.scrape.return_value = page("https://a.com/", "# A")
    (doc,) = reader.load_data(url="https://a.com")

    for mode in (MetadataMode.EMBED, MetadataMode.LLM):
        content = doc.get_content(metadata_mode=mode)
        assert "url: https://a.com/" in content
        assert "job_id" not in content
        assert "cached" not in content


def test_scrape_many_batches_ten_at_a_time_keeps_order_and_skips_failures(
    caplog: pytest.LogCaptureFixture,
) -> None:
    reader, client = make_reader("scrape", country="gb")
    urls = [f"https://a.com/{i}" for i in range(12)]

    def scrape_batch(chunk: list[str], **_: Any) -> BatchScrapeResult:
        items = [
            {"index": i, "id": f"job_{url}", "url": url, "status": "completed", "markdown": url}
            for i, url in enumerate(chunk)
        ]
        if "https://a.com/3" in chunk:
            items[3] = {"index": 3, "url": "https://a.com/3", "status": "failed", "error": "403"}
        # The API may list results out of order; the reader sorts by index.
        return BatchScrapeResult.model_validate(
            {"id": f"batch_{len(chunk)}", "status": "completed", "results": items[::-1]}
        )

    client.scrape_batch.side_effect = scrape_batch
    with caplog.at_level(logging.WARNING, logger="llama_index.readers.anakin.base"):
        docs = reader.load_data(urls=urls)

    assert [d.text for d in docs] == [u for u in urls if u != "https://a.com/3"]
    assert [d.id_ for d in docs] == [d.text for d in docs]
    assert [c.args[0] for c in client.scrape_batch.call_args_list] == [urls[:10], urls[10:]]
    assert all(c.kwargs == {"country": "gb"} for c in client.scrape_batch.call_args_list)
    assert "https://a.com/3" in caplog.text
    assert "403" in caplog.text
    assert "batch_10" in caplog.text


def test_scrape_many_rejects_options_the_batch_api_does_not_take() -> None:
    reader, _ = make_reader("scrape", force_fresh=True)
    with pytest.raises(TypeError, match="force_fresh"):
        reader.load_data(urls=["https://a.com"])


def test_failed_single_scrape_raises() -> None:
    reader, client = make_reader("scrape")
    client.scrape.side_effect = JobFailedError("Scrape job failed", job_id="job_1")
    with pytest.raises(JobFailedError):
        reader.load_data(url="https://a.com")


def test_crawl_returns_completed_pages_and_logs_the_rest(
    caplog: pytest.LogCaptureFixture,
) -> None:
    reader, client = make_reader("crawl", max_pages=5, include_patterns=["/docs/*"])
    client.crawl.return_value = CrawlResult.model_validate(
        {
            "id": "c1",
            "url": "https://a.com",
            "results": [
                {"url": "https://a.com/x", "status": "completed", "markdown": "page x"},
                {"url": "https://a.com/y", "status": "failed", "error": "blocked"},
                {"url": "https://a.com/z", "status": "completed", "markdown": ""},
            ],
        }
    )
    with caplog.at_level(logging.WARNING, logger="llama_index.readers.anakin.base"):
        docs = reader.load_data(url="https://a.com")

    assert [(d.text, d.id_) for d in docs] == [("page x", "https://a.com/x")]
    assert docs[0].metadata["crawl_url"] == "https://a.com"
    assert "https://a.com/y" in caplog.text
    assert "blocked" in caplog.text
    assert "https://a.com/z" in caplog.text
    client.crawl.assert_called_once_with("https://a.com", max_pages=5, include_patterns=["/docs/*"])


def test_search_documents_carry_title_snippet_and_url() -> None:
    reader, client = make_reader("search", limit=2)
    client.search.return_value = SearchResult.model_validate(
        {
            "id": "s1",
            "results": [
                {"url": "https://a.com", "title": "A", "snippet": "about a", "date": "2026-10-01"},
                {"url": "https://b.com", "snippet": "only a snippet"},
            ],
        }
    )
    docs = reader.load_data(query="what is a")
    assert [d.text for d in docs] == ["A\n\nabout a", "only a snippet"]
    assert docs[0].metadata["url"] == "https://a.com"
    assert docs[0].metadata["date"] == "2026-10-01"
    assert docs[0].metadata["query"] == "what is a"
    client.search.assert_called_once_with("what is a", limit=2)


def test_map_returns_one_document_per_link() -> None:
    reader, client = make_reader("map", search="blog", limit=50)
    client.map.return_value = MapResult.model_validate(
        {
            "id": "m1",
            "url": "https://a.com",
            "links": ["https://a.com/blog/1", "https://a.com/blog/2"],
        }
    )
    docs = reader.load_data(url="https://a.com")
    assert [d.text for d in docs] == ["https://a.com/blog/1", "https://a.com/blog/2"]
    assert docs[0].metadata["site_url"] == "https://a.com"
    client.map.assert_called_once_with("https://a.com", search="blog", limit=50)


@pytest.mark.parametrize(
    ("mode", "kwargs", "message"),
    [
        ("scrape", {}, "url or urls"),
        ("scrape", {"url": "https://a.com", "urls": ["https://b.com"]}, "not both"),
        ("crawl", {}, "needs url"),
        ("map", {"query": "x"}, "needs url"),
        ("search", {"url": "https://a.com"}, "needs query"),
    ],
)
def test_missing_input_is_a_clear_error(mode: str, kwargs: dict[str, Any], message: str) -> None:
    reader, client = make_reader(mode)
    with pytest.raises(ValueError, match=message):
        reader.load_data(**kwargs)
    assert not client.method_calls


def test_unknown_mode_is_rejected() -> None:
    with pytest.raises(ValueError, match="mode"):
        AnakinWebReader(api_key="ask_test", mode="extract")  # type: ignore[arg-type]
