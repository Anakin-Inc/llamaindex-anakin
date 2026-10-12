# Changelog

## 0.1.0 (unreleased)

- `AnakinWebReader` with `scrape`, `crawl`, `search` and `map` modes.
- Several URLs are scraped 10 at a time in parallel. Pages that fail are logged
  and skipped.
- Scraped and crawled pages use their URL as the Document ID.
