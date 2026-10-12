# llama-index-tools-anakin

LlamaIndex tools for [Anakin](https://anakin.io): scrape, search, map and crawl
the web, run deep research, use pre-built Wire actions on hundreds of sites,
monitor pages for changes, compare AI answer engines and drive a cloud browser.

`AnakinToolSpec` has all 22 tools of Anakin's hosted MCP server
(`mcp.anakin.io`), with the same names, built on the official
[`anakin-sdk`](https://pypi.org/project/anakin-sdk/) client.

## Install

```bash
pip install llama-index-tools-anakin
export ANAKIN_API_KEY=...   # free at https://anakin.io/dashboard
```

## Use with an agent

```python
import asyncio

from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.anthropic import Anthropic
from llama_index.tools.anakin import AnakinToolSpec

agent = FunctionAgent(
    tools=AnakinToolSpec().to_tool_list(),
    llm=Anthropic(model="claude-opus-5-5"),
    system_prompt="Answer with facts from the web. Cite the pages you used.",
)


async def main() -> None:
    print(await agent.run("What do the top three CRM vendors charge per seat?"))


asyncio.run(main())
```

Any LlamaIndex LLM that supports function calling works.

To give the agent fewer tools (and a shorter prompt), pick them by name:

```python
tools = AnakinToolSpec().to_tool_list(spec_functions=["search", "scrape", "crawl"])
```

## Options

```python
AnakinToolSpec(
    api_key=None,  # defaults to ANAKIN_API_KEY
    read_only=False,  # True leaves out the 7 tools that change something
    allow_financial_actions=False,  # see "Payments" below
    poll_timeout=600.0,  # seconds to wait for scrapes, crawls and research
    client=None,  # or pass your own anakin.Anakin client
)
```

**`read_only=True`** leaves out the tools that change something on a website or
in the user's Anakin account, or that start a long paid job: `wire_write_action`,
`wire_login`, `wire_build`, `monitor_create`, `monitor_control`, `session_delete`
and `browser_task`. Use it for agents that should only look things up.

**Payments.** Like the hosted MCP server, `wire_write_action`, `wire_build` and
`browser_task` refuse anything that looks like it completes a payment or moves
money (pay, checkout, purchase, place order, buy now, wire transfer, payout).
Adding to a cart or filling in a form is allowed. Pass
`allow_financial_actions=True` to turn the check off.

## Tools

| Tool | What it does |
|---|---|
| **Web data** | |
| `scrape` | One page as clean markdown, optionally with AI-extracted JSON |
| `search` | Web search: URLs, titles and snippets, returned immediately |
| `map` | Every URL on a site, to decide what to crawl |
| `crawl` | Many pages of one site as markdown |
| `agentic_search` | Deep research across many sources, as a summary plus structured data |
| **Wire: pre-built site actions** | |
| `wire_discover` | Find actions for a task, e.g. "top phones on walmart" |
| `wire_catalog` | Every supported site, or one site's actions and their parameters |
| `wire_read_action` | Run an action that reads data |
| `wire_write_action` | Run an action that changes something on the site * |
| `wire_identities` | The user's saved site logins (credentials) |
| `wire_login` | Sign in to a site and get a credential * |
| `wire_build` | Ask Wire to build actions for a site it doesn't cover yet * |
| `wire_build_status` | Progress of those builds |
| **Monitors** | |
| `monitor_create` | Watch a page, a site or a Wire action on a schedule * |
| `monitor_list` | The user's monitors, or one monitor's settings |
| `monitor_changes` | Changes a monitor detected |
| `monitor_control` | Pause, resume, run now or delete a monitor * |
| **AI visibility** | |
| `ai_visibility_search` | Ask ChatGPT, Gemini and Google AI Overview the same question and compare |
| `ai_visibility_sources` | The answer engines available |
| **Browser** | |
| `session_list` | Saved browser logins, for pages behind a sign-in |
| `session_delete` | Delete a saved browser login * |
| `browser_task` | An AI agent that drives a real browser through a multi-step task * |

\* Left out by `read_only=True`.

Each tool's description and parameter docs go to the model in the function
schema. Descriptions stay under the 1,024 characters LlamaIndex allows for
OpenAI function definitions.

## Errors and timeouts

Tools raise the SDK's exceptions, such as `anakin.AuthenticationError`,
`anakin.InsufficientCreditsError`, `anakin.RateLimitError` and
`anakin.JobFailedError`. All of them subclass `anakin.AnakinError`, and
LlamaIndex agents pass the message back to the model. Scrapes, crawls and
research wait up to `poll_timeout` seconds. A browser task waits up to 6
minutes.

Agents call these tools in a worker thread, so they don't block an async event
loop.

## Development

```bash
uv sync
uv run pytest
uv run ruff check . && uv run ruff format --check . && uv run mypy llama_index
```

## License

MIT
