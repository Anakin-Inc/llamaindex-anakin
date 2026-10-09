"""Anakin tool spec: the full Anakin API as LlamaIndex agent tools."""

import inspect
import os
import re
import time
from collections.abc import Callable
from typing import Any, Literal
from urllib.parse import quote

import httpx
from anakin import Anakin
from anakin.errors import AnakinError
from llama_index.core.tools import FunctionTool, ToolMetadata
from llama_index.core.tools.tool_spec.base import SPEC_FUNCTION_TYPE, BaseToolSpec
from pydantic import BaseModel, Field, create_model

DEFAULT_BASE_URL = "https://api.anakin.io/v1"

# Tools that change something: on a website, in the user's Anakin account, or
# that spend credits on a long-running job. `read_only=True` leaves them out.
WRITE_TOOLS = (
    "wire_write_action",
    "wire_login",
    "wire_build",
    "monitor_create",
    "monitor_control",
    "session_delete",
    "browser_task",
)

# Same guard as Anakin's hosted MCP server: refuse Wire writes, Wire builds and
# browser tasks that look like they complete a payment or move money. Targets
# payment completion (pay, checkout, purchase, place order, transfers), not
# "add to cart".
_FINANCIAL = re.compile(
    r"\b(payments?|pay\s?now|checkout|purchase|place\s?order|buy\s?now|wire\s?transfer"
    r"|remit(?:tance)?|payout|charge\s?card|transfer\s?funds)\b",
    re.IGNORECASE,
)

BROWSER_TASK_POLL_SECONDS = 3.0
BROWSER_TASK_MAX_SECONDS = 360.0

# An "Args:" entry in a tool docstring: "    name: text", continued on lines
# indented further.
_ARG_LINE = re.compile(r"^ {4}(\w+): (.+)$")


def _jsonable(value: Any) -> Any:
    """SDK models (pydantic) and containers of them, as plain JSON-ready data."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", by_alias=False, exclude_none=True)
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    return value


def _looks_financial(*parts: Any) -> bool:
    text = " ".join(str(p) for p in parts if p is not None)
    # \b does not split snake_case or kebab-case ids such as "shop_checkout".
    return bool(_FINANCIAL.search(re.sub(r"[_-]+", " ", text)))


def _tool_metadata(name: str, fn: Callable[..., Any]) -> ToolMetadata:
    """
    A tool's metadata: the docstring summary as its description, and its
    parameters with their "Args:" text as a JSON schema.

    LlamaIndex's default description is the whole signature plus docstring,
    which runs past the 1024 characters `to_openai_tool()` allows for the
    larger tools, and it only reads parameter docs written "name (type): text".
    """
    summary, _, args = inspect.cleandoc(fn.__doc__ or "").partition("\nArgs:\n")
    docs: dict[str, str] = {}
    current = None
    for line in args.splitlines():
        match = _ARG_LINE.match(line)
        if match:
            current = match.group(1)
            docs[current] = match.group(2)
        elif current and line.strip():
            docs[current] += " " + line.strip()
    fields: dict[str, Any] = {
        param.name: (
            param.annotation,
            Field(
                default=... if param.default is inspect.Parameter.empty else param.default,
                description=docs.get(param.name),
            ),
        )
        for param in inspect.signature(fn).parameters.values()
    }
    return ToolMetadata(
        name=name,
        description=" ".join(summary.split()),
        fn_schema=create_model(name, **fields),
    )


class AnakinToolSpec(BaseToolSpec):
    """
    Anakin tool spec: scrape, search, map, crawl, deep research, Wire site
    actions, website monitors, AI-engine answer comparison, saved browser
    sessions and AI-driven browser tasks. https://anakin.io
    """

    # BaseToolSpec declares this as an instance-overridable list; read_only
    # replaces it per instance, so it can't be a ClassVar.
    spec_functions = [  # noqa: RUF012
        "scrape",
        "search",
        "map",
        "crawl",
        "agentic_search",
        "wire_discover",
        "wire_catalog",
        "wire_read_action",
        "wire_write_action",
        "wire_identities",
        "wire_login",
        "wire_build",
        "wire_build_status",
        "monitor_create",
        "monitor_list",
        "monitor_changes",
        "monitor_control",
        "ai_visibility_search",
        "ai_visibility_sources",
        "session_list",
        "session_delete",
        "browser_task",
    ]

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        read_only: bool = False,
        allow_financial_actions: bool = False,
        poll_timeout: float = 600.0,
        client: Anakin | None = None,
    ) -> None:
        """
        Args:
            api_key: Anakin API key. Defaults to the ANAKIN_API_KEY environment variable.
                Get one free at https://anakin.io/dashboard.
            base_url: Anakin API base URL.
            read_only: Leave out every tool that changes something or starts a
                long-running paid job (see WRITE_TOOLS).
            allow_financial_actions: Allow Wire writes, Wire builds and browser
                tasks that look like a payment or money transfer. Off by default.
            poll_timeout: Seconds to wait for async jobs (scrape, crawl, research).
            client: An existing `anakin.Anakin` client to use instead.
        """
        self._api_key = api_key if api_key is not None else os.environ.get("ANAKIN_API_KEY")
        self._base_url = base_url.rstrip("/")
        self._allow_financial = allow_financial_actions
        self.client = client or Anakin(
            api_key=api_key, base_url=self._base_url, poll_timeout=poll_timeout
        )
        if read_only:
            self.spec_functions = [f for f in self.spec_functions if f not in WRITE_TOOLS]

    def to_tool_list(
        self,
        spec_functions: list[SPEC_FUNCTION_TYPE] | None = None,
        func_to_metadata_mapping: dict[str, ToolMetadata] | None = None,
    ) -> list[FunctionTool]:
        """Convert the spec to FunctionTools with short descriptions and documented parameters."""
        names = spec_functions or self.spec_functions
        metadata = {
            name: _tool_metadata(name, getattr(self, name))
            for name in names
            if isinstance(name, str)
        }
        metadata.update(func_to_metadata_mapping or {})
        return super().to_tool_list(spec_functions, metadata)

    # ── Web data ──────────────────────────────────────────────────────────

    def scrape(
        self,
        url: str,
        country: str = "us",
        use_browser: bool = False,
        generate_json: bool = False,
        force_fresh: bool = False,
        session_id: str | None = None,
        session_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch one web page and return its content as clean markdown.

        Use for a single known URL. Check wire_discover first for well-known sites
        (Amazon, LinkedIn, Zillow, ...): a Wire action returns structured data directly.

        Args:
            url: The page to fetch (http or https).
            country: Two-letter country to fetch from, for geo-specific content.
            use_browser: Render with a headless browser. Only for JavaScript-heavy pages;
                slower and costs more.
            generate_json: Also extract structured fields with AI.
            force_fresh: Skip the 24-hour cache.
            session_id: Saved browser session (from session_list) for pages behind a
                login. Use with use_browser=True.
            session_name: A saved browser session's name, instead of session_id.
        """
        doc = self.client.scrape(
            url,
            country=country,
            use_browser=use_browser,
            generate_json=generate_json,
            force_fresh=force_fresh,
            session_id=session_id,
            session_name=session_name,
        )
        return _jsonable(doc)

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        Search the web and return result URLs, titles and snippets. Returns
        immediately; scrape the results worth reading in full.

        Args:
            query: What to search for, in natural language.
            limit: Number of results (1-20).
        """
        return _jsonable(self.client.search(query, limit=limit).results)

    def map(
        self,
        url: str,
        limit: int = 100,
        depth: int = 2,
        limit_per_level: int = 100,
        search: str | None = None,
        include_subdomains: bool = False,
        include_external_links: bool = False,
        use_browser: bool = False,
    ) -> dict[str, Any]:
        """
        List the URLs on a website. Use before crawl to decide which pages matter.

        Args:
            url: The site or section to start from.
            limit: Maximum URLs to return (up to 1000).
            depth: Link hops to follow from the start URL (up to 5).
            limit_per_level: Maximum URLs collected per link hop (up to 1000).
            search: Only return URLs whose path or title matches this keyword.
            include_subdomains: Also follow links to subdomains.
            include_external_links: Also return links to other sites.
            use_browser: Render pages with a headless browser (for single-page apps).
        """
        result = self.client.map(
            url,
            limit=limit,
            depth=depth,
            limit_per_level=limit_per_level,
            search=search,
            include_subdomains=include_subdomains,
            include_external_links=include_external_links,
            use_browser=use_browser,
        )
        return _jsonable(result)

    def crawl(
        self,
        url: str,
        max_pages: int = 10,
        depth: int = 1,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        country: str = "us",
        use_browser: bool = False,
        session_id: str | None = None,
        session_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetch many pages of one site as markdown, each with its own status.

        Scope it with include_patterns; an unscoped crawl spends credits on
        navigation and archive pages.

        Args:
            url: Where to start.
            max_pages: Hard cap on pages fetched (up to 500); the main cost lever.
            depth: Link hops to follow (up to 5).
            include_patterns: Only crawl URLs matching these glob or regex patterns.
            exclude_patterns: Skip URLs matching these patterns.
            country: Two-letter country to fetch from.
            use_browser: Render with a headless browser.
            session_id: Saved browser session for pages behind a login.
            session_name: A saved browser session's name, instead of session_id.
        """
        result = self.client.crawl(
            url,
            max_pages=max_pages,
            depth=depth,
            include_patterns=include_patterns or (),
            exclude_patterns=exclude_patterns or (),
            country=country,
            use_browser=use_browser,
            session_id=session_id,
            session_name=session_name,
        )
        return _jsonable(result)

    def agentic_search(
        self,
        prompt: str,
        output_schema: dict[str, Any] | None = None,
        use_browser: bool = True,
    ) -> dict[str, Any]:
        """
        Research a question across many sources: searches, reads the citations
        and returns a summary plus structured data. Takes 1-5 minutes.

        Use when one page or a list of links can't answer the question
        (comparisons, market research). Pass a JSON Schema to get typed output.

        Args:
            prompt: The research question, as specific as possible.
            output_schema: Optional JSON Schema for the structured result.
            use_browser: Render cited pages with a headless browser.
        """
        result = self.client.agentic_search(prompt, schema=output_schema, use_browser=use_browser)
        return _jsonable(result)

    # ── Wire: pre-built site actions ──────────────────────────────────────

    def wire_discover(
        self, query: str, site: str | None = None, limit: int = 5
    ) -> list[dict[str, Any]]:
        """
        Find pre-built Wire actions for a task, ranked by relevance.

        Wire covers hundreds of popular sites with tested actions that return
        structured data, faster and cheaper than scraping or a browser task.
        Each match includes its action_id, parameters, type (read or write),
        auth requirements and credit cost.

        Args:
            query: The task, e.g. "top phones on walmart" or "a linkedin profile's work history".
            site: Limit to one catalog slug, e.g. "amazon".
            limit: Number of matches.
        """
        return _jsonable(self.client.wire.discover(query, catalog=site, limit=limit))

    def wire_catalog(self, slug: str | None = None) -> Any:
        """
        Browse the Wire catalog. Without a slug, lists every supported site; with
        one (e.g. "walmart"), lists that site's actions with exact parameter
        schemas, type (read/write), auth mode, credit cost and login fields.

        Args:
            slug: Catalog slug to inspect. Omit to list all sites.
        """
        if slug:
            return _jsonable(self.client.wire.catalog(slug))
        return _jsonable(self.client.wire.catalogs())

    def wire_read_action(
        self,
        action_id: str,
        params: dict[str, Any] | None = None,
        credential_id: str | None = None,
        identity_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Run a Wire READ action: extracts data and changes nothing on the site
        (search listings, product details, profiles, dashboard data).

        Confirm the action's type is "read" with wire_discover or wire_catalog first.

        Args:
            action_id: The action to run.
            params: Parameters matching the action's schema.
            credential_id: Credential for actions that need a login (from wire_identities).
            identity_id: Alternative to credential_id: an identity whose credential to use.
        """
        result = self.client.wire.run(
            action_id, params or {}, credential_id=credential_id, identity_id=identity_id
        )
        return _jsonable(result)

    def wire_write_action(
        self,
        action_id: str,
        params: dict[str, Any] | None = None,
        credential_id: str | None = None,
        identity_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Run a Wire WRITE action: changes state on the site (submits a form, adds
        to a cart, posts content, updates settings). Confirm with the user before
        calling. Payments and money transfers are refused.

        Args:
            action_id: The action to run (type "write").
            params: Parameters matching the action's schema.
            credential_id: Credential for the user's account on that site.
            identity_id: Alternative to credential_id.
        """
        self._refuse_if_financial("action", action_id, params)
        result = self.client.wire.run(
            action_id, params or {}, credential_id=credential_id, identity_id=identity_id
        )
        return _jsonable(result)

    def wire_identities(self, catalog_id: str | None = None) -> list[dict[str, Any]]:
        """
        List saved Wire identities and their credentials. A credential's id is the
        credential_id to pass to Wire actions that need a login; check that its
        status is "active".

        Args:
            catalog_id: Only identities for this catalog.
        """
        return _jsonable(self.client.wire.identities(catalog_id=catalog_id))

    def wire_login(
        self,
        catalog_slug: str,
        params: dict[str, Any] | None = None,
        identity_name: str | None = None,
        source_id: str | None = None,
        source_ref: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Sign in to a site for the user and get a credential_id usable right away.
        Only sign in to accounts the user owns, with details the user provided;
        never invent credentials. The password is not stored, only an encrypted session.

        Args:
            catalog_slug: The site's catalog slug.
            params: Login fields from the catalog's login_input_schema (e.g. email, password).
            identity_name: Name for the identity (required with source_id).
            source_id: A connected 1Password identity source, instead of params.
            source_ref: The 1Password item locator {vault_id, item_id, fields}.
        """
        result = self.client.wire.login(
            catalog_slug,
            params=params,
            identity_name=identity_name,
            source_id=source_id,
            source_ref=source_ref,
        )
        return _jsonable(result)

    def wire_build(
        self,
        website_url: str,
        goal: str,
        actions: list[str] | None = None,
        catalog_id: str | None = None,
        country: str | None = None,
        credential: dict[str, Any] | None = None,
        visibility: Literal["private", "public"] | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """
        Request new Wire actions for a site not yet in the catalog. Wire builds and
        tests them; track progress with wire_build_status. Charges credits (refunded
        if the build fails); a login build costs much more, so confirm with the
        user first. Only use after wire_discover and wire_catalog find nothing.

        Args:
            website_url: The site to build for.
            goal: What the action should extract or do, specifically.
            actions: Separate capabilities to build as separate actions.
            catalog_id: Add to an existing catalog instead of creating one.
            country: Two-letter country for geo-gated sites.
            credential: Login for actions behind a sign-in:
                {"type": "plain", "username": ..., "password": ...}. Used once, not stored.
            visibility: "private" (default) or "public".
            force: Build even if similar actions exist.
        """
        self._refuse_if_financial("build", goal, website_url, actions)
        result = self.client.wire.build(
            website_url,
            goal,
            actions=actions,
            catalog_id=catalog_id,
            country=country,
            credential=credential,
            visibility=visibility,
            force=force,
        )
        return _jsonable(result)

    def wire_build_status(
        self,
        build_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> Any:
        """
        Check Wire builds. With build_id, returns that build: its status (poll
        about every 30 seconds while "pending" or "processing"), the published
        actions and a skipped list of anything it could not deliver. Without
        build_id, lists recent builds.

        Args:
            build_id: The id from wire_build's response.
            status: List mode only: filter by status.
            limit: List mode only: maximum builds per page.
            page: List mode only: 1-based page, to see builds past the first page.
        """
        if build_id:
            return _jsonable(self.client.wire.get_build(build_id))
        return _jsonable(self.client.wire.builds(status=status, page=page, limit=limit))

    # ── Monitors ──────────────────────────────────────────────────────────

    def monitor_create(
        self,
        url: str,
        interval_minutes: int,
        scope: Literal["page", "site", "wire"] = "page",
        watch_mode: Literal["full_page", "specific_data"] = "full_page",
        watch_format: Literal["markdown", "html", "cleaned_html"] | None = None,
        output_schema: dict[str, Any] | None = None,
        ai_mode: bool = False,
        ai_goal: str | None = None,
        alert_webhook_url: str | None = None,
        alert_emails: list[str] | None = None,
        use_browser: bool = False,
        country: str | None = None,
        session_id: str | None = None,
        max_pages: int | None = None,
        max_depth: int | None = None,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        wire_action_id: str | None = None,
        wire_catalog_slug: str | None = None,
        wire_params: dict[str, Any] | None = None,
        wire_credential_id: str | None = None,
        wire_watch_paths: list[str] | None = None,
        is_active: bool | None = None,
        expires_at: str | None = None,
    ) -> dict[str, Any]:
        """
        Watch a page, a whole site or a Wire action on a schedule and record
        changes, optionally alerting a webhook or email. Every check costs
        credits: full_page 2, specific_data 3, ai_mode +1. Tell the user the
        credits per day ((1440 / interval_minutes) x cost per check) before creating.

        Args:
            url: The page or site to watch (for wire scope, the site's URL).
            interval_minutes: Minutes between checks (minimum 15).
            scope: "page", "site" (tracks pages added, removed, changed) or "wire".
            watch_mode: "full_page", or "specific_data" to track only output_schema fields.
            watch_format: full_page mode: compare "markdown" (default), "html" or "cleaned_html".
            output_schema: JSON Schema of fields to track (required for specific_data).
            ai_mode: Filter out trivial changes and summarize real ones.
            ai_goal: With ai_mode, which changes count, e.g. "only price drops".
            alert_webhook_url: Webhook to notify on change.
            alert_emails: Emails to notify on change.
            use_browser: Render with a headless browser.
            country: Two-letter country to check from.
            session_id: Saved browser session for pages behind a login.
            max_pages: Site scope: pages per check.
            max_depth: Site scope: link depth to crawl (1-5, default 2).
            include_patterns: Site scope: only these URLs.
            exclude_patterns: Site scope: skip these URLs.
            wire_action_id: Wire scope: the action to run each check.
            wire_catalog_slug: Wire scope: the action's catalog slug.
            wire_params: Wire scope: the action's parameters.
            wire_credential_id: Wire scope: credential for actions behind a login.
            wire_watch_paths: Wire scope: JSON paths to compare instead of the whole result.
            is_active: False creates the monitor paused.
            expires_at: Date the monitor pauses itself (ISO 8601 or YYYY-MM-DD).
        """
        options: dict[str, Any] = {
            "scope": scope,
            "watch_mode": watch_mode,
            "watch_format": watch_format,
            "output_schema": output_schema,
            "ai_mode": ai_mode,
            "ai_goal": ai_goal,
            "alert_webhook_url": alert_webhook_url,
            "alert_emails": alert_emails,
            "use_browser": use_browser,
            "country": country,
            "session_id": session_id,
            "max_pages": max_pages,
            "max_depth": max_depth,
            "include_patterns": include_patterns,
            "exclude_patterns": exclude_patterns,
            "wire_action_id": wire_action_id,
            "wire_catalog_slug": wire_catalog_slug,
            "wire_params": wire_params,
            "wire_credential_id": wire_credential_id,
            "wire_watch_paths": wire_watch_paths,
            "is_active": is_active,
            "expires_at": expires_at,
        }
        options = {k: v for k, v in options.items() if v is not None}
        return _jsonable(self.client.monitors.create(url, interval_minutes, **options))

    def monitor_list(self, monitor_id: str | None = None) -> Any:
        """
        List the user's monitors, or with monitor_id, one monitor's settings and
        status (next and last check, active state, cost per check, alerts).

        Args:
            monitor_id: Return just this monitor.
        """
        if monitor_id:
            return _jsonable(self.client.monitors.get(monitor_id))
        return _jsonable(self.client.monitors.list())

    def monitor_changes(self, monitor_id: str) -> list[dict[str, Any]]:
        """
        Get the changes a monitor detected, each with its diff or summary.

        Args:
            monitor_id: The monitor (from monitor_list or monitor_create).
        """
        return _jsonable(self.client.monitors.changes(monitor_id))

    def monitor_control(
        self,
        monitor_id: str,
        action: Literal["pause", "resume", "run_now", "delete"],
    ) -> dict[str, Any]:
        """
        Pause, resume, run now or delete a monitor. run_now is billed like a check.
        delete permanently removes the monitor and its history: confirm with the
        user first.

        Args:
            monitor_id: The monitor.
            action: "pause", "resume", "run_now" or "delete".
        """
        monitors = self.client.monitors
        if action == "pause":
            return _jsonable(monitors.pause(monitor_id))
        if action == "resume":
            return _jsonable(monitors.resume(monitor_id))
        if action == "run_now":
            return _jsonable(monitors.run_now(monitor_id))
        if action == "delete":
            monitors.delete(monitor_id)
            return {"id": monitor_id, "deleted": True}
        raise ValueError(f'Unknown action "{action}": use pause, resume, run_now or delete.')

    # ── AI Visibility ─────────────────────────────────────────────────────

    def ai_visibility_search(
        self,
        query: str,
        sources: list[str] | None = None,
        country: str = "us",
        include_full_content: bool = False,
    ) -> dict[str, Any]:
        """
        Ask several AI answer engines (such as ChatGPT, Gemini and Google AI
        Overview) the same question and compare their answers, with a synthesis
        of where they agree. For brand and AI-SEO visibility checks. Takes 1-2
        minutes; billed per engine.

        Args:
            query: The question to ask every engine.
            sources: Engine slugs to ask (see ai_visibility_sources). Default: all enabled.
            country: Two-letter country for geo-specific answers.
            include_full_content: Also return each engine's full answer, which is
                long. Summaries and the synthesis are always returned.
        """
        result = _jsonable(
            self.client.ai_visibility.search(query, sources=sources, country=country)
        )
        if not include_full_content:
            for engine in result.get("results", []):
                engine.pop("full_content", None)
        return result

    def ai_visibility_sources(self) -> list[dict[str, Any]]:
        """List the AI answer engines ai_visibility_search can ask, with their slugs."""
        return _jsonable(self.client.ai_visibility.sources())

    # ── Saved browser sessions and browser tasks ──────────────────────────

    def session_list(self, domain: str | None = None) -> list[dict[str, Any]]:
        """
        List the user's saved browser sessions (encrypted login states created in
        the Anakin dashboard). Pass a session's id as session_id to scrape, crawl,
        monitor_create or browser_task to reach pages behind that login.

        Args:
            domain: Only sessions for this site, e.g. "amazon.com".
        """
        return _jsonable(self.client.sessions.list(domain=domain))

    def session_delete(self, session_id: str) -> dict[str, Any]:
        """
        Permanently delete a saved browser session. The user must log in again in
        the dashboard to recreate it, and monitors using it lose access. Confirm
        with the user first.

        Args:
            session_id: The session to delete (from session_list).
        """
        self.client.sessions.delete(session_id)
        return {"id": session_id, "deleted": True}

    def browser_task(
        self,
        prompt: str,
        url: str | None = None,
        session_id: str | None = None,
        output_schema: dict[str, Any] | None = None,
        max_steps: int | None = None,
        timeout_ms: int | None = None,
    ) -> Any:
        """
        Have an AI agent drive a real cloud browser for a multi-step task
        (navigate, click, type, extract). Runs up to about 5 minutes. Use only
        when scrape can't do it and no Wire action exists. Never put passwords in
        the prompt: use session_id. Payments are refused.

        Args:
            prompt: The task, specific about the goal and what to return.
            url: Where to start.
            session_id: Saved browser session for logged-in tasks.
            output_schema: JSON Schema for a structured result.
            max_steps: Cap on browser steps.
            timeout_ms: Task timeout in milliseconds.
        """
        self._refuse_if_financial("task", prompt, url)
        body: dict[str, Any] = {"prompt": prompt, "async": True}
        optional = {
            "url": url,
            "session_id": session_id,
            "output_schema": output_schema,
            "max_steps": max_steps,
            "timeout_ms": timeout_ms,
        }
        body.update({k: v for k, v in optional.items() if v is not None})

        with httpx.Client(
            base_url=self._base_url,
            headers={"X-API-Key": self._api_key or ""},
            timeout=30.0,
        ) as http:
            accepted = self._api(http, "POST", "/ai/evaluate", json=body)
            workflow_id = accepted.get("workflow_id")
            if not workflow_id:
                return accepted
            deadline = time.monotonic() + BROWSER_TASK_MAX_SECONDS
            while time.monotonic() < deadline:
                job = self._api(http, "GET", f"/ai/jobs/{quote(str(workflow_id), safe='')}")
                status = job.get("status")
                if status == "completed":
                    return job.get("result", job)
                if status in ("failed", "timed_out"):
                    raise AnakinError(
                        f"Browser task {status}: {job.get('error') or 'unknown error'}",
                        code=str(status).upper(),
                    )
                time.sleep(BROWSER_TASK_POLL_SECONDS)
        raise AnakinError("Browser task still running after 6 minutes.", code="TIMEOUT")

    def _refuse_if_financial(self, kind: str, *parts: Any) -> None:
        if not self._allow_financial and _looks_financial(*parts):
            raise ValueError(
                f"Refused: this {kind} looks like a payment or money transfer. Complete "
                "payments directly on the site, or create the tool spec with "
                "allow_financial_actions=True."
            )

    def _api(self, http: httpx.Client, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        if not self._api_key:
            raise AnakinError(
                "No Anakin API key: pass api_key or set ANAKIN_API_KEY. "
                "Get one free at https://anakin.io/dashboard."
            )
        try:
            res = http.request(method, path, **kwargs)
        except httpx.HTTPError as err:
            raise AnakinError(f"Could not reach the Anakin API: {err}") from err
        try:
            data = res.json() if res.content else {}
        except ValueError:
            data = {}
        if res.status_code >= 400:
            detail = data.get("message") or data.get("error") if isinstance(data, dict) else None
            if isinstance(detail, dict):
                detail = detail.get("message")
            raise AnakinError(
                detail or f"Anakin API returned {res.status_code}",
                status_code=res.status_code,
                body=data,
            )
        return data if isinstance(data, dict) else {"result": data}
