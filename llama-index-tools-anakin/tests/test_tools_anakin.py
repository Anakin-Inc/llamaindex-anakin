import asyncio
import inspect
from typing import Any
from unittest.mock import create_autospec

import httpx
import pytest
from anakin import Anakin
from anakin.errors import AnakinError
from anakin.models import AIVisibilitySearch, Document, SearchResult
from llama_index.core.tools import FunctionTool
from llama_index.core.tools.tool_spec.base import BaseToolSpec

from llama_index.tools.anakin import WRITE_TOOLS, AnakinToolSpec, base

# Every tool on Anakin's hosted MCP server (mcp.anakin.io), by the same name.
ALL_TOOLS = {
    "scrape", "search", "map", "crawl", "agentic_search",
    "wire_discover", "wire_catalog", "wire_read_action", "wire_write_action",
    "wire_identities", "wire_login", "wire_build", "wire_build_status",
    "monitor_create", "monitor_list", "monitor_changes", "monitor_control",
    "ai_visibility_search", "ai_visibility_sources",
    "session_list", "session_delete", "browser_task",
}  # fmt: skip

# Each hosted MCP tool's parameters, in snake_case (mcp.anakin.io, October 2026).
HOSTED_PARAMS = {
    "scrape": {"url", "country", "use_browser", "generate_json", "force_fresh",
               "session_id", "session_name"},
    "search": {"prompt", "limit"},
    "map": {"url", "limit", "depth", "limit_per_level", "search", "include_subdomains",
            "include_external_links", "use_browser"},
    "crawl": {"url", "max_pages", "depth", "include_patterns", "exclude_patterns", "country",
              "use_browser", "session_id", "session_name"},
    "agentic_search": {"prompt", "schema", "use_browser"},
    "wire_discover": {"q", "limit"},
    "wire_catalog": {"slug"},
    "wire_read_action": {"action_id", "params", "credential_id", "identity_id"},
    "wire_write_action": {"action_id", "params", "credential_id", "identity_id"},
    "wire_identities": {"catalog_id"},
    "wire_login": {"catalog_slug", "params", "identity_name", "source_id", "source_ref"},
    "wire_build": {"website_url", "goal", "actions", "catalog_id", "country", "credential",
                   "visibility", "force"},
    "wire_build_status": {"id", "status", "limit", "page", "include_events"},
    "monitor_create": {"url", "interval_minutes", "scope", "watch_mode", "watch_format",
                       "output_schema", "ai_mode", "ai_goal", "alert_webhook_url",
                       "alert_emails", "use_browser", "country", "session_id", "max_pages",
                       "max_depth", "include_patterns", "exclude_patterns", "wire_action_id",
                       "wire_catalog_slug", "wire_params", "wire_credential_id",
                       "wire_watch_paths", "is_active", "expires_at"},
    "monitor_list": {"id"},
    "monitor_changes": {"id"},
    "monitor_control": {"id", "action"},
    "ai_visibility_search": {"query", "sources", "country", "include_full_content"},
    "ai_visibility_sources": set(),
    "session_list": {"domain"},
    "session_delete": {"id"},
    "browser_task": {"prompt", "url", "session_id", "output_schema", "max_steps", "timeout_ms"},
}  # fmt: skip
# Where this package names a hosted parameter differently.
RENAMED = {
    ("search", "prompt"): "query",
    ("agentic_search", "schema"): "output_schema",  # `schema` shadows a pydantic attribute
    ("wire_discover", "q"): "query",
    ("wire_build_status", "id"): "build_id",
    ("monitor_list", "id"): "monitor_id",
    ("monitor_changes", "id"): "monitor_id",
    ("monitor_control", "id"): "monitor_id",
    ("session_delete", "id"): "session_id",
}
# Hosted parameters the Python SDK has no option for.
NOT_IN_SDK = {("wire_build_status", "include_events")}


@pytest.fixture
def client() -> Any:
    # Autospec a real client, so a call that doesn't match the SDK's signature fails.
    return create_autospec(Anakin(api_key="ask_test"))


@pytest.fixture
def spec(client: Any) -> AnakinToolSpec:
    return AnakinToolSpec(api_key="ask_test", client=client)


def test_is_a_tool_spec() -> None:
    assert BaseToolSpec.__name__ in [b.__name__ for b in AnakinToolSpec.__mro__]


def test_exposes_every_anakin_tool(spec: AnakinToolSpec) -> None:
    assert set(spec.spec_functions) == ALL_TOOLS
    assert len(spec.spec_functions) == 22


def test_tools_take_every_hosted_mcp_parameter(spec: AnakinToolSpec) -> None:
    assert set(HOSTED_PARAMS) == ALL_TOOLS
    for tool, hosted in HOSTED_PARAMS.items():
        taken = set(inspect.signature(getattr(spec, tool)).parameters)
        expected = {RENAMED.get((tool, p), p) for p in hosted if (tool, p) not in NOT_IN_SDK}
        assert expected <= taken, f"{tool} is missing {sorted(expected - taken)}"


def test_every_tool_converts_with_a_description(spec: AnakinToolSpec) -> None:
    tools = spec.to_tool_list()
    assert {t.metadata.name for t in tools} == ALL_TOOLS
    for tool in tools:
        assert isinstance(tool, FunctionTool)
        assert len(tool.metadata.description) > 60, tool.metadata.name
        assert tool.metadata.fn_schema is not None


def test_tool_metadata_fits_openai_and_documents_every_parameter(spec: AnakinToolSpec) -> None:
    for tool in spec.to_tool_list():
        meta = tool.metadata
        # Raises when a description is over 1024 characters.
        parameters = meta.to_openai_tool()["function"]["parameters"]
        taken = set(inspect.signature(getattr(spec, meta.name)).parameters)
        assert set(parameters["properties"]) == taken, meta.name
        for param, schema in parameters["properties"].items():
            assert schema.get("description"), f"{meta.name}.{param} has no description"
        assert "Args:" not in meta.description


def test_monitor_create_schema_requires_url_and_interval(spec: AnakinToolSpec) -> None:
    tools = {t.metadata.name: t for t in spec.to_tool_list()}
    parameters = tools["monitor_create"].metadata.get_parameters_dict()
    assert sorted(parameters["required"]) == ["interval_minutes", "url"]
    assert "minimum 15" in parameters["properties"]["interval_minutes"]["description"]


def test_read_only_drops_exactly_the_write_tools(client: Any) -> None:
    spec = AnakinToolSpec(api_key="k", client=client, read_only=True)
    assert set(spec.spec_functions) == ALL_TOOLS - set(WRITE_TOOLS)
    assert {t.metadata.name for t in spec.to_tool_list()} == ALL_TOOLS - set(WRITE_TOOLS)
    # The class default is untouched for other instances.
    assert len(AnakinToolSpec.spec_functions) == 22


def test_scrape_returns_the_sdk_document_as_plain_data(spec: AnakinToolSpec, client: Any) -> None:
    client.scrape.return_value = Document.model_validate(
        {
            "id": "job_1",
            "url": "https://example.com/",
            "status": "completed",
            "markdown": "# Example",
            "durationMs": 1200,
            "cached": True,
        }
    )
    out = spec.scrape("https://example.com", use_browser=True, session_id="s1")
    client.scrape.assert_called_once_with(
        "https://example.com", country="us", use_browser=True,
        generate_json=False, force_fresh=False, session_id="s1", session_name=None,
    )  # fmt: skip
    assert out["markdown"] == "# Example"
    assert out["duration_ms"] == 1200
    assert "html" not in out  # None fields are dropped


def test_search_returns_results(spec: AnakinToolSpec, client: Any) -> None:
    client.search.return_value = SearchResult.model_validate(
        {"id": "s", "results": [{"url": "https://a.com", "title": "A"}]}
    )
    assert spec.search("crm pricing", limit=3) == [{"url": "https://a.com", "title": "A"}]
    client.search.assert_called_once_with("crm pricing", limit=3)


def test_tool_call_goes_through_llamaindex(spec: AnakinToolSpec, client: Any) -> None:
    client.search.return_value = SearchResult.model_validate(
        {"id": "s", "results": [{"url": "https://a.com", "title": "A"}]}
    )
    tool = {t.metadata.name: t for t in spec.to_tool_list()}["search"]
    output = tool.call(query="crm pricing")
    assert "https://a.com" in output.content


# FunctionAgent's own internals touch deprecated pydantic attributes.
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_function_agent_calls_a_tool_and_reads_its_result(
    spec: AnakinToolSpec, client: Any
) -> None:
    mock_llms = pytest.importorskip("llama_index.core.llms.mock")
    if not hasattr(mock_llms, "MockFunctionCallingLLM"):
        pytest.skip("this llama-index-core has no MockFunctionCallingLLM")
    from llama_index.core.agent.workflow import FunctionAgent
    from llama_index.core.base.llms.types import ChatMessage, MessageRole, ToolCallBlock

    client.search.return_value = SearchResult.model_validate(
        {"id": "s", "results": [{"url": "https://a.com/pricing", "title": "A pricing"}]}
    )

    def respond(messages: list[ChatMessage], **_: Any) -> ChatMessage:
        results = [m for m in messages if m.role == MessageRole.TOOL]
        if results:
            return ChatMessage(role=MessageRole.ASSISTANT, content=f"Found {results[-1].content}")
        call = ToolCallBlock(
            tool_call_id="call_1", tool_name="search", tool_kwargs={"query": "crm pricing"}
        )
        return ChatMessage(role=MessageRole.ASSISTANT, blocks=[call])

    agent = FunctionAgent(
        tools=spec.to_tool_list(),
        llm=mock_llms.MockFunctionCallingLLM(response_generator=respond),
    )

    async def run() -> Any:
        return await agent.run("What does CRM software cost?")

    assert "https://a.com/pricing" in str(asyncio.run(run()))
    client.search.assert_called_once_with("crm pricing", limit=5)


@pytest.mark.parametrize(
    ("method", "kwargs", "sdk_path", "expected"),
    [
        ("map", {"url": "https://a.com", "search": "blog"}, "map",
         (("https://a.com",), {"limit": 100, "depth": 2, "limit_per_level": 100, "search": "blog",
          "include_subdomains": False, "include_external_links": False, "use_browser": False})),
        ("crawl", {"url": "https://a.com", "include_patterns": ["/docs/*"]}, "crawl",
         (("https://a.com",), {"max_pages": 10, "depth": 1, "include_patterns": ["/docs/*"],
          "exclude_patterns": (), "country": "us", "use_browser": False, "session_id": None,
          "session_name": None})),
        ("agentic_search", {"prompt": "q", "output_schema": {"type": "object"}}, "agentic_search",
         (("q",), {"schema": {"type": "object"}, "use_browser": True})),
        ("wire_discover", {"query": "phones", "site": "walmart"}, "wire.discover",
         (("phones",), {"catalog": "walmart", "limit": 5})),
        ("wire_catalog", {}, "wire.catalogs", ((), {})),
        ("wire_catalog", {"slug": "amazon"}, "wire.catalog", (("amazon",), {})),
        ("wire_read_action", {"action_id": "amazon.search", "params": {"q": "tv"}}, "wire.run",
         (("amazon.search", {"q": "tv"}), {"credential_id": None, "identity_id": None})),
        ("wire_identities", {"catalog_id": "c1"}, "wire.identities", ((), {"catalog_id": "c1"})),
        ("wire_login", {"catalog_slug": "neb", "params": {"email": "e"}}, "wire.login",
         (("neb",), {"params": {"email": "e"}, "identity_name": None, "source_id": None,
          "source_ref": None})),
        ("wire_build", {"website_url": "https://x.com", "goal": "list jobs", "country": "US"},
         "wire.build",
         (("https://x.com", "list jobs"), {"actions": None, "catalog_id": None, "country": "US",
          "credential": None, "visibility": None, "force": False})),
        ("wire_build_status", {"build_id": "b1"}, "wire.get_build", (("b1",), {})),
        ("wire_build_status", {"status": "pending", "limit": 5, "page": 2}, "wire.builds",
         ((), {"status": "pending", "page": 2, "limit": 5})),
        ("monitor_list", {}, "monitors.list", ((), {})),
        ("monitor_list", {"monitor_id": "m1"}, "monitors.get", (("m1",), {})),
        ("monitor_changes", {"monitor_id": "m1"}, "monitors.changes", (("m1",), {})),
        ("ai_visibility_search", {"query": "best crm", "sources": ["chatgpt"]},
         "ai_visibility.search", (("best crm",), {"sources": ["chatgpt"], "country": "us"})),
        ("ai_visibility_sources", {}, "ai_visibility.sources", ((), {})),
        ("session_list", {"domain": "amazon.com"}, "sessions.list", ((), {"domain": "amazon.com"})),
    ],
)  # fmt: skip
def test_tools_call_the_matching_sdk_method(
    spec: AnakinToolSpec,
    client: Any,
    method: str,
    kwargs: dict[str, Any],
    sdk_path: str,
    expected: Any,
) -> None:
    target = client
    for part in sdk_path.split("."):
        target = getattr(target, part)
    target.return_value = {"ok": True}
    assert getattr(spec, method)(**kwargs) == {"ok": True}
    args, kw = expected
    target.assert_called_once_with(*args, **kw)


def test_monitor_create_sends_only_the_options_given(spec: AnakinToolSpec, client: Any) -> None:
    client.monitors.create.return_value = {"id": "m1"}
    spec.monitor_create(
        "https://a.com", 60, watch_mode="specific_data",
        output_schema={"type": "object"}, ai_mode=True, ai_goal="price drops",
    )  # fmt: skip
    client.monitors.create.assert_called_once_with(
        "https://a.com", 60, scope="page", watch_mode="specific_data",
        output_schema={"type": "object"}, ai_mode=True, ai_goal="price drops", use_browser=False,
    )  # fmt: skip


def test_monitor_create_passes_site_wire_and_schedule_options(
    spec: AnakinToolSpec, client: Any
) -> None:
    client.monitors.create.return_value = {"id": "m1"}
    spec.monitor_create(
        "https://a.com", 30, scope="site", watch_format="cleaned_html", max_depth=3,
        wire_catalog_slug="amazon", wire_watch_paths=["$.price"], is_active=False,
        expires_at="2026-12-31",
    )  # fmt: skip
    client.monitors.create.assert_called_once_with(
        "https://a.com", 30, scope="site", watch_mode="full_page", watch_format="cleaned_html",
        ai_mode=False, use_browser=False, max_depth=3, wire_catalog_slug="amazon",
        wire_watch_paths=["$.price"], is_active=False, expires_at="2026-12-31",
    )  # fmt: skip


def test_ai_visibility_search_leaves_out_full_answers_unless_asked(
    spec: AnakinToolSpec, client: Any
) -> None:
    client.ai_visibility.search.return_value = AIVisibilitySearch.model_validate(
        {
            "search_id": "v1",
            "status": "completed",
            "synthesis": "Both name Anakin.",
            "results": [
                {
                    "source": "chatgpt",
                    "status": "completed",
                    "summary": "s",
                    "full_content": "x" * 50,
                }
            ],
        }
    )
    short = spec.ai_visibility_search("best scraping api")
    assert short["synthesis"] == "Both name Anakin."
    assert short["results"][0]["summary"] == "s"
    assert "full_content" not in short["results"][0]
    full = spec.ai_visibility_search("best scraping api", include_full_content=True)
    assert full["results"][0]["full_content"] == "x" * 50


@pytest.mark.parametrize("action", ["pause", "resume", "run_now"])
def test_monitor_control_dispatches(spec: AnakinToolSpec, client: Any, action: str) -> None:
    getattr(client.monitors, action).return_value = {"id": "m1"}
    assert spec.monitor_control("m1", action) == {"id": "m1"}  # type: ignore[arg-type]
    getattr(client.monitors, action).assert_called_once_with("m1")


def test_monitor_control_delete_and_unknown(spec: AnakinToolSpec, client: Any) -> None:
    assert spec.monitor_control("m1", "delete") == {"id": "m1", "deleted": True}
    client.monitors.delete.assert_called_once_with("m1")
    with pytest.raises(ValueError, match="Unknown action"):
        spec.monitor_control("m1", "archive")  # type: ignore[arg-type]


def test_session_delete(spec: AnakinToolSpec, client: Any) -> None:
    assert spec.session_delete("s1") == {"id": "s1", "deleted": True}
    client.sessions.delete.assert_called_once_with("s1")


@pytest.mark.parametrize(
    ("action_id", "params"),
    [
        ("shop_checkout", {}),
        ("shop.place-order", {}),
        ("bank.send", {"note": "wire transfer to vendor"}),
        ("store.order", {"step": "buy now"}),
    ],
)
def test_write_actions_that_look_like_payments_are_refused(
    spec: AnakinToolSpec, client: Any, action_id: str, params: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="payment"):
        spec.wire_write_action(action_id, params)
    client.wire.run.assert_not_called()


def test_ordinary_write_actions_and_reads_run(spec: AnakinToolSpec, client: Any) -> None:
    client.wire.run.return_value = {"status": "completed"}
    spec.wire_write_action("shop.add_to_cart", {"sku": "1"}, credential_id="c1")
    client.wire.run.assert_called_once_with(
        "shop.add_to_cart", {"sku": "1"}, credential_id="c1", identity_id=None
    )
    # Reads are never blocked, whatever their name.
    spec.wire_read_action("shop.checkout_page_prices")
    assert client.wire.run.call_count == 2


def test_financial_guard_can_be_turned_off(client: Any) -> None:
    spec = AnakinToolSpec(api_key="k", client=client, allow_financial_actions=True)
    client.wire.run.return_value = {"status": "completed"}
    spec.wire_write_action("shop_checkout")
    client.wire.run.assert_called_once()


def test_wire_build_refuses_payment_builds(spec: AnakinToolSpec, client: Any) -> None:
    with pytest.raises(ValueError, match="payments"):
        spec.wire_build("https://shop.example", "complete checkout with saved card")
    client.wire.build.assert_not_called()


# ── browser_task talks to the REST API directly ───────────────────────────


def _mock_api(
    monkeypatch: pytest.MonkeyPatch, responses: list[httpx.Response]
) -> list[httpx.Request]:
    seen: list[httpx.Request] = []
    queue = list(responses)

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return queue.pop(0)

    real_client = httpx.Client
    monkeypatch.setattr(
        base.httpx,
        "Client",
        lambda **kw: real_client(transport=httpx.MockTransport(handler), **kw),
    )
    monkeypatch.setattr(base.time, "sleep", lambda _: None)
    return seen


def test_browser_task_starts_then_polls_until_completed(
    spec: AnakinToolSpec, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = _mock_api(
        monkeypatch,
        [
            httpx.Response(202, json={"workflow_id": "wf_1", "status": "queued"}),
            httpx.Response(200, json={"status": "running"}),
            httpx.Response(200, json={"status": "completed", "result": {"price": "$9"}}),
        ],
    )
    assert spec.browser_task("find the price", url="https://a.com", max_steps=10) == {"price": "$9"}
    assert seen[0].method == "POST"
    assert seen[0].url.path == "/v1/ai/evaluate"
    assert seen[0].headers["X-API-Key"] == "ask_test"
    assert b'"async":true' in seen[0].content.replace(b" ", b"")
    assert b'"max_steps":10' in seen[0].content.replace(b" ", b"")
    assert seen[1].url.path == "/v1/ai/jobs/wf_1"


@pytest.mark.parametrize(
    ("prompt", "url"),
    [
        ("Buy now the cheapest TV and pay with the saved card", None),
        ("Finish the order", "https://shop.example/checkout"),
        ("Send a wire transfer of $500 to this account", None),
    ],
)
def test_browser_task_refuses_payment_tasks_before_calling_the_api(
    spec: AnakinToolSpec, monkeypatch: pytest.MonkeyPatch, prompt: str, url: str | None
) -> None:
    seen = _mock_api(monkeypatch, [])
    with pytest.raises(ValueError, match="payment"):
        spec.browser_task(prompt, url=url)
    assert seen == []


def test_browser_task_failure_raises(spec: AnakinToolSpec, monkeypatch: pytest.MonkeyPatch) -> None:
    _mock_api(
        monkeypatch,
        [
            httpx.Response(202, json={"workflow_id": "wf_1"}),
            httpx.Response(200, json={"status": "failed", "error": "page blocked"}),
        ],
    )
    with pytest.raises(AnakinError, match="page blocked"):
        spec.browser_task("do it")


def test_browser_task_api_error_is_reported(
    spec: AnakinToolSpec, monkeypatch: pytest.MonkeyPatch
) -> None:
    _mock_api(monkeypatch, [httpx.Response(401, json={"message": "Invalid API key"})])
    with pytest.raises(AnakinError, match="Invalid API key") as info:
        spec.browser_task("do it")
    assert info.value.status_code == 401


def test_browser_task_needs_a_key(client: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANAKIN_API_KEY", raising=False)
    spec = AnakinToolSpec(client=client)
    with pytest.raises(AnakinError, match="No Anakin API key"):
        spec.browser_task("do it")
