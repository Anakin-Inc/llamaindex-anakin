# Changelog

## 0.1.0 (unreleased)

- `AnakinToolSpec` with all 22 tools of Anakin's hosted MCP server, under the
  same names: web data, Wire actions and builds, monitors, AI visibility, saved
  browser sessions and browser tasks.
- `read_only=True` leaves out the 7 tools that change something.
- Wire writes, Wire builds and browser tasks refuse payments and money
  transfers unless `allow_financial_actions=True`.
- Short tool descriptions with per-parameter docs in the function schema, so
  every tool works with OpenAI-style function calling.
