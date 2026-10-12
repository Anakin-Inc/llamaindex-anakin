# llama-index-readers-anakin

Load web content into LlamaIndex with [Anakin](https://anakin.io). Scrape
pages, crawl a site, take web search results or a site's URL map, and get
LlamaIndex `Document`s ready to index. Built on the official
[`anakin-sdk`](https://pypi.org/project/anakin-sdk/) client.

## Install

```bash
pip install llama-index-readers-anakin
export ANAKIN_API_KEY=...   # free at https://anakin.io/dashboard
```

## Usage

```python
from llama_index.core import VectorStoreIndex
from llama_index.readers.anakin import AnakinWebReader

# Crawl a docs site into a vector index.
reader = AnakinWebReader(
    mode="crawl",
    params={"max_pages": 50, "include_patterns": ["/docs/*"]},
)
documents = reader.load_data(url="https://anakin.io/docs")
index = VectorStoreIndex.from_documents(documents)

# Scrape a list of pages, 10 at a time in parallel.
pages = AnakinWebReader().load_data(urls=["https://example.com/a", "https://example.com/b"])

# Pages that need JavaScript to render.
spa = AnakinWebReader(params={"use_browser": True}).load_data(url="https://example.com/app")
```

## Modes

| `mode` | Call | One Document per | `params` go to |
|---|---|---|---|
| `scrape` (default) | `load_data(url=...)` or `load_data(urls=[...])` | page, as markdown | `Anakin.scrape` for one URL, `Anakin.scrape_batch` for several |
| `crawl` | `load_data(url=...)` | crawled page, as markdown | `Anakin.crawl` |
| `search` | `load_data(query=...)` | search result (title and snippet) | `Anakin.search` |
| `map` | `load_data(url=...)` | URL found on the site | `Anakin.map` |

`params` takes that SDK call's keyword arguments, for example `country`,
`use_browser`, `session_id` (a saved browser login), `max_pages`, `depth`,
`include_patterns`, `exclude_patterns` or `limit`. Batch scraping takes fewer
options than single-page scraping (no `force_fresh` or `formats`), and an option
it doesn't take raises `TypeError`.

## Documents

- **IDs.** A scraped or crawled page's Document ID is its URL. Loading the same
  page again updates it in an `IngestionPipeline` with a docstore instead of
  adding a duplicate.
- **Metadata.** Each Document has `url`. Search results also have `title`,
  `date` and `query`. The bookkeeping fields (`source`, `mode`, `job_id`,
  `cached`, `crawl_url`, `site_url`) are kept out of embeddings and LLM prompts.
- **Failures.** One URL that fails raises the SDK's error, such as
  `anakin.JobFailedError`. With several URLs or a crawl, pages that fail are
  skipped and logged as warnings with their URL, status and job ID, so one
  blocked page doesn't lose the rest.

`await reader.aload_data(...)` runs the load in a worker thread.

## Development

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check . && uv run mypy llama_index
```

## License

MIT
