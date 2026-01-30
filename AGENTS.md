## LlamaAgents at a glance

LlamaAgents helps you build and deploy small, workflow‑driven agentic apps using LlamaIndex, locally and on LlamaCloud. Define LlamaIndex workflows, run them as durable APIs that can pause for input, optionally add a UI, and deploy to LlamaCloud in seconds.

LlamaAgents is for developers and teams building automation, internal tools, and app‑like agent experiences without heavy infrastructure work.

Build and ship small, focused agentic apps—fast. Start from either our templated LlamaIndex workflow apps, or from workflows you've already prototyped, iterate locally, and deploy to LlamaCloud right from your terminal in seconds.

- Write [LlamaIndex Python workflows](https://developers.llamaindex.ai/python/workflows/), and serve them as an API. For example, make a request to process incoming files, analyze them, and return the result or forward them on to another system.
- Workflow runs are durable, and can wait indefinitely for human or other external inputs before proceeding.
- Optionally add a UI for user-driven applications. Make custom chat applications, data extraction and review applications.
- Deploy your app in seconds to LlamaCloud. Call it as an API with your API key, or visit it secured with your LlamaCloud login.

LlamaAgents is built on top of LlamaIndex's (soon-to-be) open source LlamaDeploy v2. LlamaDeploy is a toolchain to create, develop, and deploy workflows. The `llamactl` command line interface (CLI) is the main point of entry to developing LlamaDeploy applications: It can scaffold LlamaDeploy based projects with `llamactl init`, serve them with `llamactl serve`, and deploy with `llamactl deployments create`.

In addition to LlamaDeploy, LlamaIndex published additional SDKs to facilitate rapid development:

- Our `llama-cloud-services` JS and Python SDKs offer a simple way to persist ad hoc Agent Data. [Read more here](https://developers.llamaindex.ai/python/cloud/llamaagents/agent-data-overview).
- Our `@llamaindex/ui` React library offers off-the-shelf components and hooks to facilitate developing workflow-driven UIs.

# Getting Started with LlamaDeploy

LlamaDeploy is composed of the [`llamactl` CLI for development](https://pypi.org/project/llamactl/). `llamactl` bootstraps an application server that manages running and persisting your workflows, and a control plane for managing cloud deployments of applications. It has some system pre-requisites that must be installed in order to work:

- Make sure you have [`uv`](https://docs.astral.sh/uv/getting-started/installation/) installed. `uv` is a Python package manager and build tool. `llamactl` integrates with it in order to quickly manage your project's build and dependencies.
- Likewise, Node.js is required for UI development. You can use your node package manager of choice (`npm`, `pnpm`, or `yarn`).

## Install

Choose one:

- Try without installing:

```bash
uvx llamactl --help
```

- Install globally (recommended):

```bash
uv tool install -U llamactl
llamactl --help
```

## Initialize a project

`llamactl` includes starter templates for both full‑stack UI apps, and headless (API only) workflows. Pick a template and customize it.

```bash
llamactl init
```

This will prompt for some details, and create a Python module that contains LlamaIndex workflows, plus an optional UI you can serve as a static frontend.

Application configuration is managed within your project's `pyproject.toml`, where you can define Python workflow instances that should be served, environment details, and configuration for how the UI should be built. See the [Deployment Config Reference](https://developers.llamaindex.ai/python/cloud/llamaagents/configuration-reference) for details on all configurable fields.

## Develop

Once you have a project, you can run the dev server for your application:

```bash
llamactl serve
```

`llamactl serve` will

1. Install all required dependencies
2. Read the workflows configured in your app’s `pyproject.toml` and serve them as an API
3. Start up and proxy the frontend development server, so you can seamlessly write a full stack application.

For example, with the following configuration, the app will be served at `http://localhost:4501/deployments/my-package`. Make a `POST` request to `/deployments/my-package/workflows/my-workflow/run` to trigger the workflow in `src/my_package/my_workflow.py`.

```toml
[project]
name = "my-package"
# ...
[tool.llamadeploy.workflows]
my-workflow = "my_package.my_workflow:workflow"

[tool.llamadeploy.ui]
directory = "ui"
```

```py
# src/my_package/my_workflow.py
# from workflows import ...
# ...
workflow = MyWorkflow()
```

At this point, you can get to coding. The development server will detect changes as you save files. It will even resume in-progress workflows!

For more information about CLI flags available, see [`llamactl serve`](https://developers.llamaindex.ai/python/cloud/llamacloud/llamadeploy/llamactl-reference/commands-serve).

For a more detailed reference on how to define and expose workflows, see [Workflows & App Server API](https://developers.llamaindex.ai/python/cloud/llamacloud/llamadeploy/workflow-api).

## Create a Deployment

LlamaDeploy applications can be rapidly deployed just by pointing to a source git repository. With the provided repository configuration, LlamaCloud will clone, build, and serve your app. It can even access GitHub private repositories by installing the [LlamaDeploy GitHub app](https://github.com/apps/llama-deploy)

Example:

```bash
git remote add origin https://github.com/org/repo
git add -A
git commit -m 'Set up new app'
git push -u origin main
```

Then, create a deployment:

```bash
llamactl deployments create
```

:::info
The first time you run this, you'll be prompted to log into LlamaCloud. See [`llamactl auth`](./llamactl-reference/commands-auth) for more info
:::

This will open an interactive Terminal UI (TUI). You can tab through fields, or even point and click with your mouse if your terminal supports it. All required fields should be automatically detected from your environment, but can be customized:

- Name: Human‑readable and URL‑safe; appears in your deployment URL
- Git repository: Public HTTP or private GitHub (install the LlamaDeploy GitHub app for private repos)
- Git branch: Branch to pull and build from (use `llamactl deployments update` to roll forward). This can also be a tag or a git commit.
- Secrets: Pre‑filled from your local `.env`; edit as needed. These cannot be read again after creation.

When you save, LlamaDeploy will verify that it has access to your repository, (and prompt you to install the GitHub app if not)

After creation, the TUI will show deployment status and logs.

- You can later use `llamactl deployments get` to view again.
- You can add secrets or change branches with `llamactl deployments edit`.
- If you update your source repo, run `llamactl deployments update` to roll a new version.

<!-- sep---sep -->

# Serving your Workflows

LlamaDeploy runs your LlamaIndex workflows locally and in the cloud. Author your workflows, add minimal configuration, and `llamactl` wraps them in an application server that exposes them as HTTP APIs.

## Learn the basics (LlamaIndex Workflows)

LlamaDeploy is built on top of LlamaIndex workflows. If you're new to workflows, start here: [LlamaIndex Workflows](https://developers.llamaindex.ai/python/workflows).

## Author a workflow (quick example)

```python
# src/app/workflows.py
from llama_index.core.workflow import Workflow, step, StartEvent, StopEvent


class QuestionFlow(Workflow):
    @step
    async def generate(self, ev: StartEvent) -> StopEvent:
        question = ev.question
        return StopEvent(result=f"Answer to {question}")


qa_workflow = QuestionFlow(timeout=120)
```

## Configure workflows for LlamaDeploy to serve

LlamaDeploy reads workflows configured in your `pyproject.toml` and makes them available under their configured names.

Define workflow instances in your code, then reference them in your config.

```toml
# pyproject.toml
[project]
name = "app"
# ...
[tool.llamadeploy.workflows]
answer-question = "app.workflows:qa_workflow"
```

## How serving works (local and cloud)

- `llamactl serve` discovers your config. See [`llamactl serve`](https://developers.llamaindex.ai/python/cloud/llamaagents/llamactl-reference/commands-serve).
- The app server loads your workflows.
- HTTP routes are exposed under `/deployments/{name}`. In development, `{name}` defaults to your Python project name and is configurable. On deploy, you can set a new name; a short random suffix may be appended to ensure uniqueness.
- Workflow instances are registered under the specified name. For example, `POST /deployments/app/workflows/answer-question/run` runs the workflow above.
- If you configure a UI, it runs alongside your API (proxied in dev, static in preview). For details, see [UI build and dev integration](https://developers.llamaindex.ai/python/cloud/llamaagents/ui-build).

During development, the API is available at `http://localhost:4501`. After you deploy to LlamaCloud, it is available at `https://api.cloud.llamaindex.ai`.

### Authorization

During local development, the API is unprotected. After deployment, your API uses the same authorization as LlamaCloud. Create an API token in the same project as the agent to make requests. For example:

```bash
curl 'https://api.cloud.llamaindex.ai/deployments/app-xyz123/workflows/answer-question/run' \
  -H 'Authorization: Bearer llx-xxx' \
  -H 'Content-Type: application/json' \
  --data '{"start_event": {"question": "What is the capital of France?"}}'
```

## Workflow HTTP API

When using a `WorkflowServer`, the app server exposes your workflows as an API. View the OpenAPI reference at `/deployments/<name>/docs`.

This API allows you to:

- Retrieve details about registered workflows
- Trigger runs of your workflows
- Stream published events from your workflows, and retrieve final results from them
- Send events to in-progress workflows (for example, HITL scenarios).

During development, visit `http://localhost:4501/debugger` to test and observe your workflows in a UI.

<!-- sep---sep -->

# Configuring a UI

This page explains how to configure a custom frontend that builds and communicates with your LlamaDeploy workflow server. If you've started from a template, you're good to go. Read on to learn more.

The LlamaDeploy toolchain is unopinionated about your UI stack — bring your own UI. Most templates use Vite with React, but any framework will work that can:

- build static assets for production, and
- read a few environment variables during build and development

## How the integration works

`llamactl` starts and proxies your frontend during development by calling your `npm run dev` command. When you deploy, it builds your UI statically with `npm run build`. These commands are configurable; see [UIConfig](https://developers.llamaindex.ai/python/cloud/llamaagents/configuration-reference#uiconfig-fields) in the configuration reference. You can also use other package managers if you have [corepack](https://nodejs.org/download/release/v19.9.0/docs/api/corepack.html) enabled.

During development, `llamactl` starts its workflow server (port `4501` by default) and starts the UI, passing a `PORT` environment variable (set to `4502` by default) and a `LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH` (for example, `/deployments/<name>/ui`) where the UI will be served. It then proxies requests from the server to the client app from that base path.

Once deployed, the Kubernetes operator builds your application with the configured npm script (`build` by default) and serves your static assets at the same base path.

## Required configuration

1. Serve the dev UI on the configured `PORT`. This environment variable tells your dev server which port to use during development. Many frameworks, such as Next.js, read this automatically.
2. Set your app's base path to the value of `LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH`. LlamaDeploy applications rely on this path to route to multiple workflow deployments. The proxy leaves this path intact so your application can link internally using absolute paths. Your development server and router need to be aware of this base path. Most frameworks provide a way to configure it. For example, Vite uses [`base`](https://vite.dev/config/shared-options.html#base).
3. Re-export the `LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH` env var to your application. Read this value (for example, in React Router) to configure a base path. This is also often necessary to link static assets correctly.
4. If you're integrating with LlamaCloud, re-export the `LLAMA_DEPLOY_PROJECT_ID` env var to your application and use it to scope your LlamaCloud requests to the same project. Read more in the [Configuration Reference](https://developers.llamaindex.ai/python/cloud/llamaagents/configuration-reference#authorization).
5. We also recommend re-exporting `LLAMA_DEPLOY_DEPLOYMENT_NAME`, which can be helpful for routing requests to your workflow server correctly.

## Examples

### Vite (React)

Configure `vite.config.ts` to read the injected environment and set the base path and port:

```ts
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(() => {
  const basePath = process.env.LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH;
  const port = process.env.PORT ? parseInt(process.env.PORT) : undefined;
  return {
    plugins: [react()],
    server: { port, host: true, hmr: { port } },
    base: basePath,
    // Pass-through env for client usage
    define: {
      ...(basePath && {
        "import.meta.env.VITE_LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH":
          JSON.stringify(basePath),
      }),
      ...(process.env.LLAMA_DEPLOY_DEPLOYMENT_NAME && {
        "import.meta.env.VITE_LLAMA_DEPLOY_DEPLOYMENT_NAME": JSON.stringify(
          process.env.LLAMA_DEPLOY_DEPLOYMENT_NAME,
        ),
      }),
      ...(process.env.LLAMA_DEPLOY_PROJECT_ID && {
        "import.meta.env.VITE_LLAMA_DEPLOY_PROJECT_ID": JSON.stringify(
          process.env.LLAMA_DEPLOY_PROJECT_ID,
        ),
      }),
    },
  };
});
```

Scripts in `package.json` typically look like:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build"
  }
}
```

### Next.js (static export)

Next.js supports static export. Configure `next.config.mjs` to use the provided base path and enable static export:

```js
// next.config.mjs
const basePath = process.env.LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH || "";
const deploymentName = process.env.LLAMA_DEPLOY_DEPLOYMENT_NAME;
const projectId = process.env.LLAMA_DEPLOY_PROJECT_ID;

export default {
  // Mount app under /deployments/<name>/ui
  basePath,
  // For assets when hosted behind a path prefix
  assetPrefix: basePath || undefined,
  // Enable static export for production
  output: "export",
  // Expose base path to browser for runtime URL construction
  env: {
    NEXT_PUBLIC_LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH: basePath,
    NEXT_PUBLIC_LLAMA_DEPLOY_DEPLOYMENT_NAME: deploymentName,
    NEXT_PUBLIC_LLAMA_DEPLOY_PROJECT_ID: projectId,
  },
};
```

Ensure your scripts export to a directory (default: `out/`):

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build && next export"
  }
}
```

The dev server binds to the `PORT` the app server sets; no additional configuration is needed. For dynamic routes or server features not compatible with static export, you can omit the export and rely on proxying to the Python app server. However, production static hosting requires a build output directory.

#### Runtime URL construction (images/assets)

- Vite: use the configured `base` or `import.meta.env.BASE_URL` (or the pass-through variable) to prefix asset URLs you build at runtime:

```tsx
const base =
  import.meta.env.VITE_LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH ||
  import.meta.env.BASE_URL ||
  "/";
<img src={`${base.replace(/\/$/, "")}/images/logo.png`} />;
```

- Next.js static export: use the exposed `NEXT_PUBLIC_LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH` so routes resolve absolute asset paths correctly:

```tsx
const base = process.env.NEXT_PUBLIC_LLAMA_DEPLOY_DEPLOYMENT_BASE_PATH || "";
export default function Logo() {
  return <img src={`${base}/images/logo.png`} alt="logo" />;
}
```

## Configure the UI output directory

Your UI must output static assets that the platform can locate. Configure `ui.directory` and `ui.build_output_dir` as described in the [Deployment Config Reference](https://developers.llamaindex.ai/python/cloud/llamaagents/configuration-reference#uiconfig-fields). Default: `${ui.directory}/dist`

<!-- sep---sep -->

# Workflow React Hooks

### `@llamaindex/ui`

Our React library, `@llamaindex/ui`, is the recommended way to integrate your UI with a LlamaDeploy workflow server and LlamaCloud. It comes pre-installed in any of our templates containing a UI. The library provides both React hooks for custom integrations and standard components.

### Workflows Hooks

Our React hooks provide an idiomatic way to observe and interact with your LlamaDeploy workflows remotely from a frontend client.

There are 3 hooks you can use:

1. **useWorkflowRun**: Start a workflow run and observe its status.
2. **useWorkflowHandler**: Observe and interact with a single run; stream and send events.
3. **useWorkflowHandlerList**: Monitor and update a list of recent or in-progress runs.

### Client setup

Configure the hooks with a workflow client. Wrap your app with an `ApiProvider` that points to your deployment:

```tsx
import {
  ApiProvider,
  type ApiClients,
  createWorkflowClient,
} from "@llamaindex/ui";

const deploymentName =
  (import.meta as any).env?.VITE_LLAMA_DEPLOY_DEPLOYMENT_NAME || "default";

const clients: ApiClients = {
  workflowsClient: createWorkflowClient({
    baseUrl: `/deployments/${deploymentName}`,
  }),
};

export function Providers({ children }: { children: React.ReactNode }) {
  return <ApiProvider clients={clients}>{children}</ApiProvider>;
}
```

### Start a run

Start a workflow by name with `useWorkflowRun`. Provide a JSON input payload. You get a `handler_id` back immediately.

```tsx
import { useState } from "react";
import { useWorkflowRun } from "@llamaindex/ui";

export function RunButton() {
  const { runWorkflow, isCreating, error } = useWorkflowRun();
  const [handlerId, setHandlerId] = useState<string | null>(null);

  async function handleClick() {
    const handler = await runWorkflow("my_workflow", { user_id: "123" });
    // e.g., navigate to a details page using handler.handler_id
    console.log("Started:", handler.handler_id);
    setHandlerId(handler.handler_id);
  }

  return (
    <>
      <button disabled={isCreating} onClick={handleClick}>
        {isCreating ? "Starting…" : "Run Workflow"}
      </button>
      {/* Then, use the handler ID to show details or send events */}
      <HandlerDetails handlerId={handlerId} />
    </>
  );
}
```

### Watch a run and stream events

Subscribe to a single handler’s live event stream and show status with `useWorkflowHandler`.

```tsx
import { useWorkflowHandler } from "@llamaindex/ui";

export function HandlerDetails({ handlerId }: { handlerId: string | null }) {
  // Note, the state will remain empty if the handler ID is empty
  const { handler, events, sendEvent } = useWorkflowHandler(
    handlerId ?? "",
    true,
  );

  // Find the final StopEvent to extract the workflow result (if provided)
  const stop = events.find(
    (e) =>
      e.type.endsWith(
        ".StopEvent",
      ) /* event type contains the event's full Python module path, e.g., workflows.events.StopEvent */,
  );

  return (
    <div>
      <div>
        <strong>{handler.handler_id}</strong> — {handler.status}
      </div>
      {stop ? (
        <pre>{JSON.stringify(stop.data, null, 2)}</pre>
      ) : (
        <pre style={{ maxHeight: 240, overflow: "auto" }}>
          {JSON.stringify(events, null, 2)}
        </pre>
      )}
    </div>
  );
}
```

You can subscribe to the same handler with multiple hooks and access a shared events list. This is useful when, for example, one component shows toast messages for certain event types while another component shows the final result.

### Monitor multiple workflow runs

Subscribe to the full list or a filtered list of workflow runs with `useWorkflowHandlerList`. This is useful for a progress indicator or a lightweight “Recent runs” view.

```tsx
import { useWorkflowHandlerList } from "@llamaindex/ui";

export function RecentRuns() {
  const { handlers, loading, error } = useWorkflowHandlerList();
  if (loading) return <div>Loading…</div>;
  if (error) return <div>Error: {error}</div>;
  return (
    <ul>
      {handlers.map((h) => (
        <li key={h.handler_id}>
          {h.handler_id} — {h.status}
        </li>
      ))}
    </ul>
  );
}
```

<!-- sep---sep -->

# Deployment Config Reference

LlamaDeploy reads configuration from your repository to run your app. The configuration is defined in your project's `pyproject.toml`.

### pyproject.toml

```toml
[tool.llamadeploy]
name = "my-app"
env_files = [".env"]

[tool.llamadeploy.workflows]
workflow-one = "my_app.workflows:some_workflow"
workflow-two = "my_app.workflows:another_workflow"

[tool.llamadeploy.ui]
directory = "ui"
build_output_dir = "ui/static"
```

### Authentication

Deployments can be configured to automatically inject authentication for LlamaCloud.

```toml
[tool.llamadeploy]
llama_cloud = true
```

When this is set:

- During development, `llamactl` prompts you to log in to LlamaCloud if you're not already. After that, it injects `LLAMA_CLOUD_API_KEY`, `LLAMA_CLOUD_PROJECT_ID`, and `LLAMA_CLOUD_BASE_URL` into your Python server process and JavaScript build.
- When deployed, LlamaCloud automatically injects a dedicated API key into the Python process. The frontend process receives a short-lived session cookie specific to each user visiting the application. Therefore, configure the project ID on the frontend API client so that LlamaCloud API requests from the frontend and backend are scoped to the same project ID.

### `.env` files

Most apps need API keys (e.g., OpenAI). You can specify them via a `.env` file and reference it in your config:

```toml
[tool.llamadeploy]
env_files = [".env"]
```

Then set your secrets:

```bash
# .env
OPENAI_API_KEY=sk-xxxx
```

### Alternative file formats (YAML/TOML)

If you prefer to keep your `pyproject.toml` simple, you can write the same configuration in a `llama_deploy.yaml` or `llama_deploy.toml` file. All fields use the same structure and types; omit the `tool.llamadeploy` prefix.

## Schema

### DeploymentConfig fields

| Field         | Type                     | Default     | Description                                                                                                   |
| ------------- | ------------------------ | ----------- | ------------------------------------------------------------------------------------------------------------- |
| `name`        | string                   | `"default"` | URL-safe deployment name. In `pyproject.toml`, if omitted it falls back to `project.name`.                    |
| `workflows`   | map&lt;string,string&gt; | —           | Map of `workflowName -> "module.path:workflow"`.                                                              |
| `env_files`   | list&lt;string&gt;       | `[".env"]`  | Paths to env files to load. Relative to the config file. Duplicate entries are removed.                       |
| `env`         | map&lt;string,string&gt; | `{}`        | Environment variables injected at runtime.                                                                    |
| `llama_cloud` | boolean                  | false       | Indicates that a deployment connects to LlamaCloud. Set to true to automatically inject a LlamaCloud API key. |
| `ui`          | `UIConfig`               | `null`      | Optional UI configuration. `directory` is required if `ui` is present.                                        |

### UIConfig fields

| Field              | Type    | Default               | Description                                                                                                                                                                                                            |
| ------------------ | ------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `directory`        | string  | —                     | Path to UI source, relative to the config directory. Required when `ui` is set.                                                                                                                                        |
| `build_output_dir` | string  | `${directory}/dist`   | Built UI output directory. If set in TOML/`pyproject.toml`, the path is relative to the config file. If set via `package.json` (`llamadeploy.build_output_dir`), it is resolved as `${directory}/${build_output_dir}`. |
| `package_manager`  | string  | `"npm"` (or inferred) | Package manager used to build the UI. If not set, inferred from `package.json` `packageManager` (e.g., `pnpm@9.0.0` → `pnpm`).                                                                                         |
| `build_command`    | string  | `"build"`             | NPM script name used to build.                                                                                                                                                                                         |
| `serve_command`    | string  | `"dev"`               | NPM script name used to serve in development.                                                                                                                                                                          |
| `proxy_port`       | integer | `4502`                | Port the app server proxies to in development.                                                                                                                                                                         |

## UI Integration via package.json

Note: after setting `ui.directory` so that `package.json` can be found, you can configure the UI within it instead.

For example:

```json
{
  "name": "my-ui",
  "packageManager": "pnpm@9.7.0",
  "scripts": { "build": "vite build", "dev": "vite" },
  "llamadeploy": {
    "build_output_dir": "dist",
    "package_manager": "pnpm",
    "build_command": "build",
    "serve_command": "dev",
    "proxy_port": 5173
  }
}
```

<!-- sep---sep -->

# Agent Data Overview

### What is Agent Data?

Skip the database setup. LlamaDeploy workflows and JavaScript UIs share a persistent Agent Data store built into the LlamaCloud API. It uses the same authentication as the rest of the API.

Agent Data is a queryable store for JSON records produced by your agents. Each record is linked to a `deployment_name` (the deployed agent) and an optional `collection` (a logical bucket; defaults to `default`). Use it to persist extractions, events, metrics, and other structured output, then search and aggregate across records.

Key concepts:

- **deployment_name**: the identifier of the agent deployment the data belongs to. Access is authorized against that agent’s project.
- **collection**: a logical namespace within an agent for organizing different data types or apps. Storage is JSON. We recommend storing homogeneous data types within a single collection.
- **data**: the JSON payload shaped by your app. SDKs provide typed wrappers.

Important behavior and constraints:

- **Deployment required**: The `deployment_name` must correspond to an existing deployment. Data is associated with that deployment and its project.
- **Local development**: When running locally, omit `deployment_name` to use the shared `_public` Agent Data store. Use distinct `collection` names to separate apps during local development.
- **Access control**: You can only read/write data for agents in projects you can access. `_public` data is visible across agents within the same project.
- **Filtering/Sorting**: You can filter on any `data` fields and on the top‑level `created_at` and `updated_at`. Sorting accepts a comma‑separated list; prefix fields inside `data` with `data.` (for example, `data.name desc, created_at`).
- **Aggregation**: Group by one or more data fields and optionally return per‑group counts and/or the first item.

Project scoping:

- You can scope requests to a specific project by providing the `Project-Id` header (UUID). This is especially important if your API key has access to multiple projects. Read more in the [Configuration Reference](https://developers.llamaindex.ai/python/cloud/llamaagents/configuration-reference#authorization).

### Filter DSL

When searching or aggregating, you can filter on fields inside `data` and on the top‑level `created_at` and `updated_at` fields.

Example:

```json
{
  "age": { "gte": 21, "lt": 65 },
  "status": { "eq": "active" },
  "tag": { "includes": ["python", "ml"] },
  "created_at": { "gte": "2024-01-01T00:00:00Z" }
}
```

Supported operators:

Filter operators are specified using a simple JSON DSL and support the following per‑field operators:

- `eq` - Filters based on equality. For example, `{"age": {"eq": 30}}` matches age exactly 30.
- `gt` - Filters based on greater than. For example, `{"age": {"gt": 30}}` matches age greater than 30.
- `gte` - Filters based on greater than or equal to. For example, `{"age": {"gte": 30}}` matches age 30 or greater.
- `lt` - Filters based on less than. For example, `{"age": {"lt": 30}}` matches age less than 30.
- `lte` - Filters based on less than or equal to. For example, `{"age": {"lte": 30}}` matches age less than or equal to 30.
- `includes` - Filters based on inclusion. For example, `{"age": {"includes": [30, 31]}}` matches age containing 30 or 31. An empty array matches nothing.

All provided filters must match (logical AND).

Nested fields are addressed using dot notation. For example, `{"data.age": {"gt": 30}}` matches an age greater than 30 in the `data` object. Note: array index access is not supported.

SDKs and environments:

- The **JavaScript SDK** can be used in the browser. When your UI is deployed on LlamaCloud alongside your agent, it is automatically authenticated. In other environments, provide an API key. You can also set `Project-Id` on the underlying HTTP client to pin all requests to a project.
- The **Python SDK** runs server‑side and uses your API key and an optional base URL.

Next steps:

- Python usage: see [Agent Data (Python)](https://developers.llamaindex.ai/python/cloud/llamaagents/agent-data-python)
- JavaScript usage: see [Agent Data (JavaScript)](https://developers.llamaindex.ai/python/cloud/llamaagents/agent-data-javascript)

<!-- sep---sep -->

# Agent Data (Python)

See the [Agent Data Overview](https://developers.llamaindex.ai/python/cloud/llamaagents/agent-data-overview) for concepts, constraints, and environment details.

### Install

```bash
uv add llama-cloud-services
```

### Client overview

The Python `llama-cloud-services` SDK provides `AsyncAgentDataClient` for working with the Agent Data API.

```python
import httpx
import os
from pydantic import BaseModel
from llama_cloud_services.beta.agent_data import AsyncAgentDataClient
from llama_cloud.client import AsyncLlamaCloud


class ExtractedPerson(BaseModel):
    name: str
    age: int
    email: str


project_id = os.getenv("LLAMA_DEPLOY_PROJECT_ID")

# Base URL and API key (if running outside LlamaCloud)
base_url = os.getenv("LLAMA_CLOUD_BASE_URL")
api_key = os.getenv("LLAMA_CLOUD_API_KEY")

# Reusable async HTTP client with optional project scoping
http_client = httpx.AsyncClient(
    headers={"Project-Id": project_id} if project_id else None
)

# Optional: base client for other SDK operations
base_client = AsyncLlamaCloud(
    base_url=base_url,
    token=api_key,
    httpx_client=http_client,
)

# Only set when deployed in LlamaCloud (falls back inside the Agent Data client)
deployment_name = os.getenv("LLAMA_DEPLOY_DEPLOYMENT_NAME")

client = AsyncAgentDataClient(
    type=ExtractedPerson,
    collection="extracted_people",
    # If omitted, uses LLAMA_DEPLOY_DEPLOYMENT_NAME or "_public"
    deployment_name=deployment_name,
    client=base_client,
)
```

### Create, Get, Update, Delete

```python
person = ExtractedPerson(name="John Doe", age=30, email="john@example.com")
created = await client.create_item(person)
fetched = await client.get_item(created.id)
updated = await client.update_item(
    created.id, ExtractedPerson(name="Jane", age=31, email="jane@example.com")
)
await client.delete_item(updated.id)
```

Retry behavior: Network errors (timeouts, connection errors, retriable HTTP statuses) are retried up to 3 times with exponential backoff.

Notes:

- Updates overwrite the entire `data` object.
- `get_item` raises an `httpx.HTTPStatusError` with status code 404 if not found.

### Search

You can filter by `data` fields and by `created_at`/`updated_at` (top-level fields). Sort using a comma-delimited list of fields; the `data.` prefix is required when sorting by data fields. The default page size is 50 (max 1000).

```python
results = await client.search(
    filter={
        # Data fields
        "age": {"gte": 21, "lt": 65},
        "status": {"eq": "active"},
        "tags": {"includes": ["python", "ml"]},
        # Top-level timestamps (ISO strings accepted)
        "created_at": {"gte": "2024-01-01T00:00:00Z"},
    },
    order_by="data.name desc, created_at",
    page_size=50,
    offset=0,
    include_total=True,  # request only on the first page if needed
)

for item in results.items:
    print(item.data)

print(results.has_more, results.total)
```

Sorting:

- Example: `"data.name desc, created_at"`.
- If no sort is provided, results default to `created_at desc`.

Pagination:

- Use `offset` and `page_size`. The server may return `has_more` and a `next_page_token` (SDK exposes `has_more`).

### Aggregate

Group data by one or more `data` fields, optionally count items per group, and/or fetch the first item per group.

```python
agg = await client.aggregate(
    filter={"status": {"eq": "active"}},
    group_by=["department", "role"],
    count=True,
    first=True,  # return the earliest item per group (by created_at)
    order_by="data.department asc, data.role asc",
    page_size=100,
)

for group in agg.items:  # items are groups
    print(group.group_key)  # {"department": "Sales", "role": "AE"}
    print(group.count)  # optional
    print(group.first_item)  # optional dict
```

Details:

- `group_by`: dot-style data paths (e.g., `"department"`, `"contact.email"`).
- `count`: adds a `count` per group.
- `first`: returns the first `data` item per group (earliest `created_at`).
- `order_by`: uses the same semantics as search (applies to group key expressions).
- Pagination uses `offset` and `page_size` similarly to search.

<!-- sep---sep -->

# Agent Data (JavaScript)

### Overview

Agent Data is a JSON store tied to a `deploymentName` and `collection`. Use the official JavaScript SDK with strong typing for CRUD, search, and aggregation.

See the [Agent Data Overview](https://developers.llamaindex.ai/python/cloud/llamaagents/agent-data-overview) for concepts, constraints, and environment details.

Install:

```bash
npm i -S llama-cloud-services
```

Key imports:

```ts
import {
  AgentClient,
  createAgentDataClient,
  type TypedAgentData,
  type TypedAgentDataItems,
  type TypedAggregateGroupItems,
  type SearchAgentDataOptions,
  type AggregateAgentDataOptions,
} from "@llama-cloud-services/beta/agent";
```

### Create client

The helper infers the `deploymentName` from environment variables or the browser URL when possible, defaulting to `"_public"`.

```ts
type Person = { name: string; age: number; email: string };

const client = createAgentDataClient<Person>({
  // Optional: infer agent from env
  env: process.env as Record<string, string>,
  // Optional: infer from browser URL when not localhost
  windowUrl: typeof window !== "undefined" ? window.location.href : undefined,
  // Optional overrides
  // deploymentName: "person-extraction-agent",
  collection: "extracted_people",
});
```

Alternatively, construct a client directly:

```ts
const direct = new AgentClient<Person>({
  // client: default (from SDK) or a custom @hey-api/client-fetch instance
  deploymentName: "person-extraction-agent",
  collection: "extracted_people",
});
```

Browser usage:

- The TypeScript SDK works in the browser. When your app is deployed in LlamaCloud alongside your agent, requests are automatically authenticated.
- In other environments (local dev, custom hosting), provide an API key to the underlying client.
- To scope to a specific project, set `Project-Id` on the client’s headers.

### CRUD operations

```ts
// Create
const created = await client.createItem({
  name: "John",
  age: 30,
  email: "john@example.com",
});

// Get (returns null on 404)
const item = await client.getItem(created.id);

// Update (overwrites data)
const updated = await client.updateItem(created.id, {
  name: "Jane",
  age: 31,
  email: "jane@example.com",
});

// Delete
await client.deleteItem(updated.id);
```

SDK responses are strongly typed and camel‑cased.

- `TypedAgentData<T>` fields: `id`, `deploymentName`, `collection?`, `data`, `createdAt`, `updatedAt`.

### Search

```ts
const options: SearchAgentDataOptions = {
  filter: {
    age: { gte: 21, lt: 65 },
    status: { eq: "active" },
    created_at: { gte: "2024-01-01T00:00:00Z" }, // top-level timestamp
  },
  orderBy: "data.name desc, created_at",
  pageSize: 50,
  offset: 0,
  includeTotal: true, // request on the first page only
};

const results: TypedAgentDataItems<Person> = await client.search(options);
for (const r of results.items) {
  console.log(r.data.name);
}
```

See the [Agent Data Overview](https://developers.llamaindex.ai/python/cloud/llamaagents/agent-data-overview#filter-dsl) for more details on filters.

- Filter keys target `data` fields, except `created_at`/`updated_at` which are top-level.
- Sort with comma-separated specs; prefix data fields in `orderBy` (e.g., `"data.name desc, created_at"`).
- Default `pageSize` is 50 (max 1000). Use `includeTotal` only on the first page.

Pagination: The default page size is 50 (max 1000). The response may include `nextPageToken` and `totalSize`.

### Aggregate

```ts
const aggOptions: AggregateAgentDataOptions = {
  filter: { status: { eq: "active" } },
  groupBy: ["department", "role"],
  count: true,
  first: true, // earliest by created_at per group
  orderBy: "data.department asc, data.role asc",
  pageSize: 100,
};

const groups: TypedAggregateGroupItems<Person> =
  await client.aggregate(aggOptions);
for (const g of groups.items) {
  console.log(g.groupKey, g.count, g.firstItem);
}
```


---


# LlamaIndex

> LlamaIndex is a framework for building data-backed LLM applications, specializing in agentic workflows and Retrieval-Augmented Generation (RAG) that connect language models to your private data.

<!-- sep---sep -->

## What is LlamaIndex?

LlamaIndex enables developers to build AI applications that combine Large Language Models with real-world data sources. The framework is specifically designed for applications that need to work with private, proprietary, or domain-specific data.

LlamaIndex addresses the fundamental challenge that LLMs are trained on public data with knowledge cutoffs, but most valuable business applications require access to private documents, databases, APIs, and real-time information. LlamaIndex bridges this gap through agentic workflows and Retrieval-Augmented Generation (RAG) techniques.

<!-- sep---sep -->

## Agentic Applications

When an LLM is used within an application to make decisions, take actions, and/or interact with the world, this is the core definition of an **agentic application**.

Key characteristics of agentic applications include:

- **LLM Augmentation**: The LLM is augmented with tools (arbitrary callable functions in code), memory, and/or dynamic prompts
- **Prompt Chaining**: Several LLM calls are used that build on each other, with the output of one LLM call being used as the input to the next
- **Routing**: The LLM is used to route the application to the next appropriate step or state
- **Parallelism**: The application can perform multiple steps or actions in parallel
- **Orchestration**: A hierarchical structure of LLMs is used to orchestrate lower-level actions and LLMs
- **Reflection**: The LLM is used to reflect and validate outputs of previous steps or LLM calls

**Agents**: An agent is a piece of software that semi-autonomously performs tasks by combining LLMs with other tools and memory, orchestrated in a reasoning loop that decides which tool to use next. An agent receives a user message, uses an LLM to determine the next appropriate action using previous chat history and tools, may invoke tools to assist with the request, interprets tool outputs, and returns the final output to the user.

**Workflows**: A Workflow in LlamaIndex is an event-driven abstraction that allows you to orchestrate a sequence of steps and LLM calls. Workflows can be used to implement any agentic application, and are a core component of LlamaIndex.

<!-- sep---sep -->

## Core Use Cases

LlamaIndex applications can be grouped into four main categories:

[**Agents**](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/module_guides/deploying/agents/index.mdx): An automated decision-maker powered by an LLM that interacts with the world via a set of [tools](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/module_guides/deploying/agents/tools.md). Agents can take an arbitrary number of steps to complete a given task, dynamically deciding on the best course of action rather than following pre-determined steps.

[**Workflows**](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/module_guides/workflow/index.mdx): A Workflow in LlamaIndex is a specific event-driven abstraction that allows you to orchestrate a sequence of steps and LLMs calls. Workflows can be used to implement any agentic application, and are a core component of LlamaIndex.

[**Query Engines**](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/module_guides/deploying/query_engine/index.mdx): A query engine is an end-to-end flow that allows you to ask questions over your data. It takes in a natural language query, and returns a response, along with reference context retrieved and passed to the LLM.

[**Chat Engines**](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/module_guides/deploying/chat_engines/index.mdx): A chat engine is an end-to-end flow for having a conversation with your data (multiple back-and-forth instead of a single question-and-answer).

<!-- sep---sep -->

## Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) is a core technique for building data-backed LLM applications with LlamaIndex. It allows LLMs to answer questions about your private data by providing it to the LLM at query time, rather than training the LLM on your data. To avoid sending all of your data to the LLM every time, RAG indexes your data and selectively sends only the relevant parts along with your query.

### RAG Pipeline Stages

There are five key stages within RAG:

1. **Loading**: Getting your data from where it lives - whether it's text files, PDFs, another website, a database, or an API - into your workflow. [LlamaHub](https://llamahub.ai/) provides hundreds of connectors to choose from.

2. **Indexing**: Creating a data structure that allows for querying the data. For LLMs this nearly always means creating vector embeddings, numerical representations of the meaning of your data, as well as numerous other metadata strategies.

3. **Storing**: Once your data is indexed you will almost always want to store your index, as well as other metadata, to avoid having to re-index it.

4. **Querying**: For any given indexing strategy there are many ways you can utilize LLMs and LlamaIndex data structures to query, including sub-queries, multi-step queries and hybrid strategies.

5. **Evaluation**: A critical step in any flow is checking how effective it is relative to other strategies, or when you make changes. Evaluation provides objective measures of how accurate, faithful and fast your responses to queries are.

<!-- sep---sep -->

## Key Components

**Documents and Nodes**: A [Document](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/module_guides/loading/documents_and_nodes/index.md) is a container around any data source - for instance, a PDF, an API output, or retrieve data from a database. A Node is the atomic unit of data in LlamaIndex and represents a "chunk" of a source Document.

**Indexes**: LlamaIndex helps you [index](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/module_guides/indexing/index.md) data into a structure that's easy to retrieve. This usually involves generating vector embeddings which are stored in a specialized database called a vector store.

**Retrievers**: A [retriever](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/module_guides/querying/retriever/index.mdx) defines how to efficiently retrieve relevant context from an index when given a query. Your retrieval strategy is key to the relevancy of the data retrieved and the efficiency with which it's done.

**Response Synthesizers**: A [response synthesizer](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/module_guides/querying/response_synthesizers/index.mdx) generates a response from an LLM, using a user query and a given set of retrieved text chunks.

<!-- sep---sep -->

## Getting Started

To get started with LlamaIndex:

1. **[Installation](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/getting_started/installation.mdx)**: Install LlamaIndex using pip or your preferred package manager
2. **[Basic Agent Example](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/getting_started/starter_example.mdx)**: Create a simple agent that can perform basic tasks using tools
3. **Adding RAG Capabilities**: Enhance your agent with the ability to search through documents
4. **[Advanced Features](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/understanding/index.mdx)**: Explore workflows, multi-agent systems, and production deployment

<!-- sep---sep -->

## Documentation and Resources

### Getting Started

- [Installation Guide](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/getting_started/installation.mdx) - Setup and installation instructions
- [Core Concepts](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/getting_started/concepts.mdx) - Fundamental LlamaIndex concepts and architecture
- [Starter Example /w OpenAI](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/getting_started/starter_example.mdx) - Basic agent implementation walkthrough
- [Local Models Example](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/getting_started/starter_example_local.mdx) - Running LlamaIndex locally with open-source models

<!-- sep---sep -->

### Core Module Guides

- [Loading Data](https://github.com/run-llama/llama_index/tree/main/docs/src/content/docs/framework/module_guides/loading/index.md) - Data connectors and ingestion strategies
- [Indexing](https://github.com/run-llama/llama_index/tree/main/docs/src/content/docs/framework/module_guides/indexing/index.md) - Vector, graph, and keyword indexing approaches
- [Querying](https://github.com/run-llama/llama_index/tree/main/docs/src/content/docs/framework/module_guides/querying/index.md) - Query engines, retrievers, and response synthesis
- [Models](https://github.com/run-llama/llama_index/tree/main/docs/src/content/docs/framework/module_guides/models/index.md) - LLM providers, embeddings, and multi-modal models
- [Storing](https://github.com/run-llama/llama_index/tree/main/docs/src/content/docs/framework/module_guides/storing/index.md) - Vector stores and storage backends
- [Workflows](https://github.com/run-llama/llama_index/tree/main/docs/src/content/docs/framework/module_guides/workflow/index.mdx) - Event-driven orchestration and complex pipelines

<!-- sep---sep -->

### Agents and Workflows

- [Building Agents](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/understanding/agent/index.mdx) - Autonomous AI systems with tool use
- [Agent Tools](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/understanding/agent/tools.md) - Available tools and how to create custom ones
- [Multi-Agent Systems](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/understanding/agent/multi_agent.md) - Collaborative agent workflows
- [Workflow Documentation](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/understanding/workflows/index.md) - Event-driven application orchestration
- [Human-in-the-Loop](https://github.com/run-llama/llama_index/blob/main/docs/src/content/docs/framework/understanding/agent/human_in_the_loop.md) - Interactive agent workflows

LlamaIndex supports dozens of LLM providers including OpenAI, Anthropic, and local models, with hundreds of data connectors for ingesting diverse data sources.


---


# High-level workflows doc for LLMs and Humans

# LlamaIndex Workflows - A Practical Compendium

## 0. Introduction

`llama-index-workflows` are an event-driven, async-first, step-based way to provide and control the execution flow of applications aimed at intelligent automation (AI agents, for instance).

## 1. Installation

You can install workflows using `pip` with:

```bash
pip install llama-index-workflows
```

or add them to a `uv` project with:

```bash
uv add llama-index-workflows
```

Once you installed them, you can use them within your code under the `workflows` namespace:

```python
from workflows import Workflow, Context, step
```

<!-- sep---sep -->

## 2. The Core Components

### 2.1 Event

`Event`is the base class for designing the events that will drive your workflow. There are five types of events:

- `StartEvent` : it’s the input event that kicks off the workflow
- `Event` : base class from which all intermediate workflow events should inherit
- `StopEvent` : last event of the workflow, should contain the output. The workflow will stop as soon as the event is returned from a step
- `InputRequiredEvent`: this event is emitted when an external input is required
- `HumanResponseEvent`: this event is emitted when a human response is returned.

> `InputRequiredEvent` and `HumanResponseEvent` are often coupled and often used to build human-in-the-loop (HITL) workflows. See the _Design Patterns_ section to gain more insight on this.

You should design the workflow around these events, and they are highly customizable (you can subclass them to add specific data transferred with them):

```python
from workflows.events import Event, StartEvent, StopEvent


class CustomStartEvent(StartEvent):
    message: str


class GreetingEvent(Event):
    greeting: str
    is_formal: bool
    time: float


class OutputEvent(StopEvent):
    output: list[str]
```

Events behave like Pydantic `BaseModel` subclasses, so their attributes can be set, modified and fetched very easily:

```python
from workflows.events import Event


class SomeEvent(Event):
    data: str


event = SomeEvent(data="hello world")
event.data = "hello universe"
print(event.data)
```

<!-- sep---sep -->

### 2.2 Context

Context is arguably the most important piece of workflows, since it holds:

- Control over statefulness execution
- Control over stored information
- Control over events emission and collection

**2.2.a Stateful execution**

Context contains a State, which is a representation of the current state of the execution flow. By default, you can access to the state and edit its property with these operations:

```python
from workflows import Workflow, Context, step


class ExampleWorkflow(Workflow):
    @step
    async def modify_state(self, ev: StartEvent, ctx: Context) -> SecondEvent:
        async with ctx.store.edit_state() as state:
            state.age = ev.age
            state.username = ev.username
            state.email = ev.email
        ## rest of the step implementation
```

You can also specify a customized model for the state, and initialize the context with that:

```python
from workflows import Workflow, Context, step
from pydantic import BaseModel


class WorkflowState(BaseModel):
    username: str
    email: str
    age: int


class ExampleWorkflow(Workflow):
    @step
    async def modify_state(
        self, ev: StartEvent, ctx: Context[WorkflowState]
    ) -> SecondEvent:
        async with ctx.store.edit_state() as state:
            state.age = ev.age
            state.username = ev.username
            state.email = ev.email
        ## rest of the step implementation
```

It is advisable to use a customized State to avoid unexpected behaviors.

<!-- sep---sep -->

**2.2.b Store**

Store is, by default, a dict-like object contained in the Context: it is mainly used for more long-term storage, and you can get and set values in this way:

```python
from workflows import Workflow, Context, step


class ExampleWorkflow(Workflow):
    @step
    async def get_set_store(self, ev: StartEvent, ctx: Context) -> SecondEvent:
        n_iterations = ctx.store.get("n_iterations", default=None)
        if n_iterations:
            n_iterations += 1
            ctx.store.set("n_iterations", n_iterations)
        else:
            ctx.store.set("n_iterations", 1)
        ## rest of the step implementation
```

Unless motivated by specific reasons, it is advisable to use `state` over `store` .

<!-- sep---sep -->

**2.2.c Emitting and collecting events**

Context can be used also to emit and collect events, as well as writing them to the event stream.

```python
class ParallelFlow(Workflow):
    @step
    async def start(self, ctx: Context, ev: StartEvent) -> StepTwoEvent | None:
        ctx.send_event(StepTwoEvent(query="Query 1"))

    @step
    async def step_two(self, ctx: Context, ev: StepTwoEvent) -> StopEvent:
        print("Running slow query ", ev.query)
        await asyncio.sleep(random.randint(1, 5))

        return StopEvent(result=ev.query)
```

As you can see, emitting an event with `ctx.send_event` sends it directly to the step that receive that event as input.

You can also implement a fan-in/fan-out pattern sending out event, having one or more worker steps that process those events, and then collecting the events with `ctx.collect_events` in a last step and emitting an output:

```python
class ConcurrentFlow(Workflow):
    @step
    async def start(
        self, ctx: Context, ev: StartEvent
    ) -> StepAEvent | StepBEvent | StepCEvent | None:
        ctx.send_event(StepAEvent(query="Query 1"))
        ctx.send_event(StepBEvent(query="Query 2"))
        ctx.send_event(StepCEvent(query="Query 3"))

    @step
    async def step_a(self, ctx: Context, ev: StepAEvent) -> StepACompleteEvent:
        print("Doing something A-ish")
        return StepACompleteEvent(result=ev.query)

    @step
    async def step_b(self, ctx: Context, ev: StepBEvent) -> StepBCompleteEvent:
        print("Doing something B-ish")
        return StepBCompleteEvent(result=ev.query)

    @step
    async def step_c(self, ctx: Context, ev: StepCEvent) -> StepCCompleteEvent:
        print("Doing something C-ish")
        return StepCCompleteEvent(result=ev.query)

    @step
    async def step_three(
        self,
        ctx: Context,
        ev: StepACompleteEvent | StepBCompleteEvent | StepCCompleteEvent,
    ) -> StopEvent:
        print("Received event ", ev.result)

        # wait until we receive 3 events
        if (
            ctx.collect_events(
                ev,
                [StepCCompleteEvent, StepACompleteEvent, StepBCompleteEvent],
            )
            is None
        ):
            return None

        # do something with all 3 results together
        return StopEvent(result="Done")
```

<!-- sep---sep -->

**2.2.d Serializing Context**

The context can be serialized into a dict. This is useful for saving state between `.run()` calls and letting steps access state store variables from previous runs, or even checkpointing state as a workflow is running.

The context is bound to a specific workflow, and tracks all the inner state and machinery needed for the runtime of the workflow.

```python
from workflows import Context

w = MyWorkflow()
ctx = Context(w)

result = await w.run(..., ctx=ctx)
# run again with access to previous state
result = await w.run(..., ctx=ctx)

# Serialize
ctx_dict = ctx.to_dict()

# Re-create
restored_ctx = Context.from_dict(w, ctx_dict)
result = await w.run(..., ctx=ctx)
```

Context serialization relies on your workflow events and workflow state store containing serializable data. If you store arbitrary objects, or don’t leverage pydantic functionalities to control serialization of state/events, you may encounter errors.

<!-- sep---sep -->

### 2.3 Resources

Resources are external dependencies injected into workflow steps. Use `Annotated[Type, Resource(factory_function)]` in step parameters to inject them.

**Example:**

```python
from workflows.resource import Resource
from llama_index.core.memory import Memory


def get_memory(*args, **kwargs):
    return Memory.from_defaults("user_id_123", token_limit=60000)


class WorkflowWithResource(Workflow):
    @step
    async def first_step(
        self,
        ev: StartEvent,
        memory: Annotated[Memory, Resource(get_memory)],
    ) -> SecondEvent:
        await memory.aput(ChatMessage(role="user", content="First step"))
        return SecondEvent(msg="Input for step 2")

    @step
    async def second_step(
        self, ev: SecondEvent, memory: Annotated[Memory, Resource(get_memory)]
    ) -> StopEvent:
        await memory.aput(ChatMessage(role="user", content=ev.msg))
        return StopEvent(result="Messages stored")
```

**Key Points:**

- Factory function return type must match declared type
- Resources are shared across steps by default (cached)
- Use `Resource(factory_func, cache=False)` to avoid steps sharing the same resource

<!-- sep---sep -->

### 2.4 The Workflow

There have been already several examples that implemented the `Workflow` class, but let’s understand it better:

- When you want to create a workflow, that has to be a subclass of the `Workflow` class
- Each of the functions of the workflow representing a step must be decorated with the `@step` decorator
- Each of the functions of the workflow must take at least an event type as an input and emit at least an event type as an output, although it is also allowed to output None. If these rules are not respected, you will encounter a validation error.
- Workflows can have linear, parallel/concurrent or cyclic execution patterns
- Every workflow instance has a timeout (by default 45 seconds): remember to set it at a higher value when needed by passing `timeout=Nseconds` when initializing your workflow (as in `wf = MyWorkflow(timeout=300)`)

Let’s see a complete example of a workflow:

```python
from workflows import Workflow, step
from workflows.events import Event, StartEvent, StopEvent

# `pip install llama-index-llms-openai` if you don't already have it
from llama_index.llms.openai import OpenAI


class JokeEvent(Event):
    joke: str


class JokeFlow(Workflow):
    llm = OpenAI()

    @step
    async def generate_joke(self, ev: StartEvent) -> JokeEvent:
        topic = ev.topic

        prompt = f"Write your best joke about {topic}."
        response = await self.llm.acomplete(prompt)
        return JokeEvent(joke=str(response))

    @step
    async def critique_joke(self, ev: JokeEvent) -> StopEvent:
        joke = ev.joke

        prompt = f"Give a thorough analysis and critique of the following joke: {joke}"
        response = await self.llm.acomplete(prompt)
        return StopEvent(result=str(response))


w = JokeFlow(timeout=60, verbose=False)
result = await w.run(topic="pirates")
print(str(result))
```

<!-- sep---sep -->

As you can see, running a workflow is an asynchronous operation. You can also create an asynchronous iterator over the events produced by the workflow (you need to explicitly emit them with `ctx.write_event_to_stream` within the workflow) and read these events _while_ they are produced:

```python
from workflows import Workflow, step, Context
from workflows.events import Event, StartEvent, StopEvent

# `pip install llama-index-llms-openai` if you don't already have it
from llama_index.llms.openai import OpenAI


class JokeEvent(Event):
    joke: str


class JokeFlow(Workflow):
    llm = OpenAI()

    @step
    async def generate_joke(self, ev: StartEvent, ctx: Context) -> JokeEvent:
        topic = ev.topic

        prompt = f"Write your best joke about {topic}."
        response = await self.llm.acomplete(prompt)
        ctx.write_event_to_stream(JokeEvent(joke=str(response)))
        return JokeEvent(joke=str(response))

    @step
    async def critique_joke(self, ev: JokeEvent, ctx: Context) -> StopEvent:
        joke = ev.joke

        prompt = f"Give a thorough analysis and critique of the following joke: {joke}"
        response = await self.llm.acomplete(prompt)
        ctx.write_event_to_stream(StopEvent(result=str(response)))
        return StopEvent(result=str(response))


async def main():
    w = JokeFlow(timeout=60, verbose=False)
    handler = w.run(topic="pirates")
    async for event in handler.stream_events():
        if isinstance(event, JokeEvent):
            print("Produced joke:", event.joke)

    result = await handler
    print(str(result))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```

<!-- sep---sep -->

## 3. Design Patterns

### 3.1 Human-In-The-Loop

Workflows support human-in-the-loop patterns using `InputRequiredEvent` and `HumanResponseEvent` during event streaming.

**Basic Implementation:**

```python
from workflows.events import InputRequiredEvent, HumanResponseEvent


class HumanInTheLoopWorkflow(Workflow):
    @step
    async def step1(self, ev: StartEvent) -> InputRequiredEvent:
        return InputRequiredEvent(prefix="Enter a number: ")

    @step
    async def step2(self, ev: HumanResponseEvent) -> StopEvent:
        return StopEvent(result=ev.response)


workflow = HumanInTheLoopWorkflow()
handler = workflow.run()

async for event in handler.stream_events():
    if isinstance(event, InputRequiredEvent):
        response = input(event.prefix)
        handler.ctx.send_event(HumanResponseEvent(response=response))

final_result = await handler
```

**Pausable Implementation:**
You can break out of the loop and resume later:

```python
handler = workflow.run()

# Pause at human input
async for event in handler.stream_events():
    if isinstance(event, InputRequiredEvent):
        break

# Handle response
response = input(event.prefix)
handler.ctx.send_event(HumanResponseEvent(response=response))

# Resume workflow
async for event in handler.stream_events():
    continue

final_result = await handler
```

The workflow waits for `HumanResponseEvent` emission and supports flexible input handling (input(), websockets, async state, etc.).

<!-- sep---sep -->

### 3.2 Branching and Looping

Workflows enable branching and looping logic more simply and flexibly than graph-based approaches.

**3.2.a Loops**

Create loops by adding custom event types and conditional returns:

```python
class LoopEvent(Event):
    loop_output: str


@step
async def step_one(self, ev: StartEvent | LoopEvent) -> FirstEvent | LoopEvent:
    if random.randint(0, 1) == 0:
        print("Bad thing happened")
        return LoopEvent(loop_output="Back to step one.")
    else:
        print("Good thing happened")
        return FirstEvent(first_output="First step complete.")
```

You can create loops from any step to any other step by defining appropriate event and return types.

**3.2.b Branches**

Branch workflows by conditionally returning different events:

```python
class BranchA1Event(Event):
    payload: str


class BranchA2Event(Event):
    payload: str


class BranchB1Event(Event):
    payload: str


class BranchB2Event(Event):
    payload: str


class BranchWorkflow(Workflow):
    @step
    async def start(self, ev: StartEvent) -> BranchA1Event | BranchB1Event:
        if random.randint(0, 1) == 0:
            return BranchA1Event(payload="Branch A")
        else:
            return BranchB1Event(payload="Branch B")

    @step
    async def step_a1(self, ev: BranchA1Event) -> BranchA2Event:
        return BranchA2Event(payload=ev.payload)

    @step
    async def step_b1(self, ev: BranchB1Event) -> BranchB2Event:
        return BranchB2Event(payload=ev.payload)

    @step
    async def step_a2(self, ev: BranchA2Event) -> StopEvent:
        return StopEvent(result="Branch A complete.")

    @step
    async def step_b2(self, ev: BranchB2Event) -> StopEvent:
        return StopEvent(result="Branch B complete.")
```

You can combine branches and loops in any order. Later sections cover running multiple branches in parallel using `send_event` and synchronizing them with `collect_events`.

<!-- sep---sep -->

### 3.3 Fan in/Fan out

Using async concurrency, users can dispatch multiple events at once, run work concurrently, and collecting the results. With workflows, this happens using the `send_event` and `collect_events` methods.

```python
class ProcessEvent(Event):
    pass


class ResultEvent(Event):
    pass


class FanInFanOut(Workflow):
    @step
    def init_run(self, ctx: Context, ev: StartEvent) -> ProcessEvent:
        await ctx.store.set("num_to_collect", len(ev.items))
        for item in ev.items:
            ctx.send_event(ProcessEvent())

    @step
    def process(self, ev: ProcessEvent) -> ResultEvent:
        await some_work()
        return ResultEvent()

    @step
    def finalize(self, ctx: Context, ev: ResultEvent) -> StopEvent | None:
        num_to_collect = await ctx.store.get("num_to_collect")
        events = ctx.collect_events(ev, [ResultEvent] * num_to_collect)
        if events is None:
            # Not enough collected yet
            return None

        await finalize_results(events)
        return StopEvent(result="Done!")
```

The `init_run` step emits several `ProcessEvent`s. The step signature is still annotated that it returns `ProcessEvent` even though it doesn't technically, in order to help validate the workflow.

`finalize()` will be triggered each time a `ResultEvent` comes in, and will only complete once all events are present.

<!-- sep---sep -->

## 4. Building Workflows with LlamaCloud Services

The following code provides you a template for building workflows with LlamaCloud Services.

This template provides the basic setup for a document processing workflow using
LlamaParse, LlamaExtract, and LLMs. The actual workflow logic should be implemented
based on your specific requirements.

```python
from pydantic import BaseModel, Field

# =============================================================================
# SETUP
# =============================================================================

# Environment Variables - assume these are already set
# os.environ["LLAMA_CLOUD_API_KEY"] = "llx-..."  # Set in environment
# os.environ["OPENAI_API_KEY"] = "sk-proj-..."   # Set in environment

# Project Configuration - these will be passed as parameters
project_id = "your-project-id"  # Replace with your project ID
organization_id = "your-organization-id"  # Replace with your organization ID

# =============================================================================
# INITIALIZE LLMS AND EMBEDDINGS
# =============================================================================

from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

# Set LLM, embedding model
embed_model = OpenAIEmbedding(model_name="text-embedding-3-small")
llm = OpenAI(model="gpt-4.1")
Settings.llm = llm
Settings.embed_model = embed_model

# =============================================================================
# INITIALIZE LLAMAPARSE
# =============================================================================

from llama_cloud_services import LlamaParse

# # Cost-Effective Mode
# llama_parser = LlamaParse(
#   # See how to get your API key at https://docs.cloud.llamaindex.ai/api_key
#   parse_mode="parse_page_with_llm",
#   high_res_ocr=True,
#   adaptive_long_table=True,
#   outlined_table_extraction=True,
#   output_tables_as_HTML=True,
#   result_type="markdown",
#   project_id=project_id,
#   organization_id=organization_id,
# )

# Agentic Mode (Default)
llama_parser = LlamaParse(
    # See how to get your API key at https://docs.cloud.llamaindex.ai/api_key
    parse_mode="parse_page_with_agent",
    model="openai-gpt-4-1-mini",
    high_res_ocr=True,
    adaptive_long_table=True,
    outlined_table_extraction=True,
    output_tables_as_HTML=True,
    result_type="markdown",
    project_id=project_id,
    organization_id=organization_id,
)

# # Agentic Plus Mode
# llama_parser = LlamaParse(
#   # See how to get your API key at https://docs.cloud.llamaindex.ai/api_key
#   parse_mode="parse_page_with_agent",
#   model="anthropic-sonnet-4.0",
#   high_res_ocr=True,
#   adaptive_long_table=True,
#   outlined_table_extraction=True,
#   output_tables_as_HTML=True,
#   result_type="markdown",
#   project_id=project_id,
#   organization_id=organization_id,
# )


# =============================================================================
# INITIALIZE LLAMAEXTRACT
# =============================================================================

from llama_cloud import ExtractConfig, ExtractMode
from llama_cloud.core.api_error import ApiError
from llama_cloud_services import LlamaExtract

# Initialize LlamaExtract
llama_extract = LlamaExtract(
    show_progress=True,
    check_interval=5,
    project_id=project_id,
    organization_id=organization_id,
)

# =============================================================================
# DEFINE YOUR DATA SCHEMA
# =============================================================================


class YourDataSchema(BaseModel):
    """Define your extraction schema here based on the task and reference files"""

    field1: str = Field(..., description="Description of field1")
    field2: float | None = Field(None, description="Description of field2")
    # Add more fields as needed based on your specific task


# Create extraction agent
extract_config = ExtractConfig(
    # Basic options
    extraction_mode=ExtractMode.MULTIMODAL,  # FAST, BALANCED, MULTIMODAL, PREMIUM
    # extraction_target=ExtractTarget.PER_DOC,   # PER_DOC, PER_PAGE
    # system_prompt="<Insert relevant context for extraction>", # set system prompt - can leave blank
    # Advanced options
    # chunk_mode=ChunkMode.PAGE,     # PAGE, SECTION
    # high_resolution_mode=True,     # Enable for better OCR
    # invalidate_cache=False,        # Set to True to bypass cache
    # Extensions (see Extensions page for details)
    # cite_sources=True,             # Enable citations
    # use_reasoning=True,            # Enable reasoning (not available in FAST mode)
    # confidence_scores=True         # Enable confidence scores (MULTIMODAL/PREMIUM only)
)

# Handle existing agent - delete if it exists
try:
    existing_agent = llama_extract.get_agent(name="YourExtractorName")
    if existing_agent:
        print("Deleting existing agent: YourExtractorName")
        # Deletion can take some time since all underlying files will be purged
        llama_extract.delete_agent(existing_agent.id)
except ApiError as e:
    if e.status_code == 404:
        pass  # Agent doesn't exist, which is fine
    else:
        raise  # Re-raise other errors

extract_agent = llama_extract.create_agent(
    "YourExtractorName", data_schema=YourDataSchema, config=extract_config
)

# =============================================================================
# WORKFLOW EVENTS
# =============================================================================

from llama_index.core.schema import TextNode
from workflows import Context, Workflow, step
from workflows.events import Event, StartEvent, StopEvent

# Import splitting functions (only needed if splitting is implemented)
# from test_utils import afind_categories_and_splits


class ParseDocEvent(Event):
    nodes: list[TextNode]


class SplitDocEvent(Event):
    splits: dict[str, list[str]]  # split_name -> list of node content


class ExtractDataEvent(Event):
    data_list: list[
        YourDataSchema
    ]  # Always a list - single item for no splitting, multiple items for splitting


# ADDITIONAL EVENTS YOU CAN DEFINE AS NEEDED, EXAMPLES BELOW (NOT EXCLUSIVE):
# class PreprocessEvent(Event):
#     """For preprocessing steps like cleaning, filtering, etc."""
#     processed_nodes: List[str]
#
# class ValidateEvent(Event):
#     """For validation steps"""
#     validated_data: YourDataSchema
#
# class TransformEvent(Event):
#     """For data transformation steps"""
#     transformed_data: Dict
#
# class AggregateEvent(Event):
#     """For aggregating results from multiple files"""
#     aggregated_results: List[YourDataSchema]

# =============================================================================
# WORKFLOW IMPLEMENTATION
# =============================================================================


class YourWorkflow(Workflow):
    def __init__(
        self,
        llama_parser: LlamaParse,
        extract_agent: LlamaExtract,
        output_file: str = "results.csv",
        verbose: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.llama_parser = llama_parser
        self.extract_agent = extract_agent
        self.output_file = output_file
        self.verbose = verbose

    @step
    async def parse_document(
        self, ctx: Context, ev: StartEvent
    ) -> ParseDocEvent:
        """
        Parse the input document using LlamaParse
        """
        # TODO: Implement document parsing
        # result = await self.llama_parser.aparse(ev.file_path)
        # markdown_nodes = await result.aget_markdown_nodes(split_by_page=True)
        # return ParseDocEvent(nodes=markdown_nodes)
        pass

    # OPTIONAL STEPS - UNCOMMENT AND IMPLEMENT AS NEEDED, EXAMPLES BELOW (NOT EXCLUSIVE)

    # @step
    # async def preprocess_document(self, ctx: Context, ev: ParseDocEvent) -> PreprocessEvent:
    #     """
    #     Preprocess the parsed document (cleaning, filtering, etc.)
    #     Use this if you need to clean or filter the parsed content
    #     """
    #     # TODO: Implement preprocessing if needed
    #     # Example: Remove headers, clean formatting, filter irrelevant sections
    #     # processed_nodes = self.clean_nodes(ev.nodes)
    #     # return PreprocessEvent(processed_nodes=processed_nodes)
    #     pass

    # @step
    # async def split_document(self, ctx: Context, ev: ParseDocEvent) -> SplitDocEvent:
    #     """
    #     Split the document into sections (only implement if task requires splitting)
    #     Use afind_categories_and_splits pattern from asset_manager_fund_analysis.md
    #     """
    #     # TODO: Implement document splitting if needed
    #     # This step is optional - only implement if the task explicitly requires splitting
    #     # Example: "split by sections", "process each chapter separately"
    #     #
    #     # from test_utils import afind_categories_and_splits
    #     #
    #     # split_description = "Find and split by each major section in this document"
    #     # split_rules = "Split by document sections, chapters, or major headings"
    #     # split_key = "section"
    #     #
    #     # splits = await afind_categories_and_splits(
    #     #     split_description,
    #     #     split_key,
    #     #     ev.nodes,
    #     #     additional_split_rules=split_rules,
    #     #     llm=llm,
    #     #     verbose=self.verbose,
    #     # )
    #     # return SplitDocEvent(splits=splits)
    #     pass

    @step
    async def extract_data(
        self, ctx: Context, ev: ParseDocEvent
    ) -> ExtractDataEvent:
        """
        Extract data from the parsed document
        """
        # TODO: Implement data extraction

        # PATTERN 1: No splitting - extract from entire document
        # combined_text = "\n".join([node.get_content(metadata_mode="all") for node in ev.nodes])
        # result_dict = (await self.extract_agent.aextract(SourceText(text_content=combined_text))).data
        # extracted_data = YourDataSchema.model_validate(result_dict)
        # return ExtractDataEvent(data_list=[extracted_data])  # Single item in list

        # PATTERN 2: With splitting - extract from each split (uncomment if splitting is implemented)
        # from llama_index.core.async_utils import run_jobs
        #
        # async def extract_from_split(split_name: str, split_nodes: List[TextNode]) -> YourDataSchema:
        #     """Extract data from a single split"""
        #     combined_text = "\n".join([node.get_content(metadata_mode="all") for node in split_nodes])
        #     result_dict = (await self.extract_agent.aextract(SourceText(text_content=combined_text))).data
        #     return YourDataSchema.model_validate(result_dict)
        #
        # # Get splits from previous step (if splitting was implemented)
        # # splits = ev.splits  # This would come from SplitDocEvent
        # # tasks = [extract_from_split(split_name, split_nodes) for split_name, split_nodes in splits.items()]
        # # extracted_data_list = await run_jobs(tasks, workers=8, show_progress=True)
        # # return ExtractDataEvent(data_list=extracted_data_list)  # Multiple items in list

        pass

    # @step
    # async def validate_data(self, ctx: Context, ev: ExtractDataEvent) -> ValidateEvent:
    #     """
    #     Validate the extracted data (optional validation step)
    #     Use this if you need to validate data quality, completeness, etc.
    #     """
    #     # TODO: Implement data validation if needed
    #     # Example: Check for required fields, validate data types, etc.
    #     # validated_data = self.validate_extracted_data(ev.data)
    #     # return ValidateEvent(validated_data=validated_data)
    #     pass

    # @step
    # async def transform_data(self, ctx: Context, ev: ExtractDataEvent) -> TransformEvent:
    #     """
    #     Transform the extracted data (optional transformation step)
    #     Use this if you need to calculate derived fields, format data, etc.
    #     """
    #     # TODO: Implement data transformation if needed
    #     # Example: Calculate growth rates, format currency, aggregate metrics
    #     # transformed_data = self.transform_extracted_data(ev.data)
    #     # return TransformEvent(transformed_data=transformed_data)
    #     pass

    @step
    async def analyze_results(
        self, ctx: Context, ev: ExtractDataEvent
    ) -> StopEvent:
        """
        Analyze and format the extracted results
        """
        # TODO: Implement result analysis and output
        # This could include creating DataFrames, saving to files, etc.

        # Always work with a list - single item for no splitting, multiple items for splitting
        # import pandas as pd
        # df = pd.DataFrame([data.dict() for data in ev.data_list])
        #
        # # Save results to file
        # df.to_csv(self.output_file, index=False)
        #
        # # Print summary if verbose
        # if self.verbose:
        #     print(f"Extracted {len(ev.data_list)} records")
        #     print(f"Results saved to: {self.output_file}")
        #     print("\nSummary:")
        #     print(df.head())
        #
        # return StopEvent(result={"dataframe": df, "raw_data": ev.data_list, "output_file": self.output_file})

        pass


# =============================================================================
# MAIN FUNCTION (EXAMPLE)
# =============================================================================


async def main():
    """
    Main function to run the workflow with configurable input files
    """
    # Set up argument parsing
    parser = argparse.ArgumentParser(
        description="Document Processing Workflow"
    )
    parser.add_argument(
        "input_files", nargs="+", help="Input files to process"
    )
    parser.add_argument(
        "--output", "-o", default="results.csv", help="Output file path"
    )
    parser.add_argument(
        "--project-id", "-p", default=project_id, help="LlamaCloud project ID"
    )
    parser.add_argument(
        "--organization-id",
        "-org",
        default=organization_id,
        help="LlamaCloud organization ID",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    # Note: project_id and organization_id are typically set at module level
    # and don't need to be updated here unless you want to override them

    print(f"Processing {len(args.input_files)} file(s)...")

    # Process each input file
    all_results = []
    for file_path in args.input_files:
        print(f"Processing: {file_path}")
        try:
            # Initialize and run workflow
            workflow = YourWorkflow(
                llama_parser=llama_parser,
                extract_agent=extract_agent,
                output_file=args.output,
                verbose=args.verbose,
                timeout=None,
            )

            result = await workflow.run(file_path=file_path)
            all_results.append(result)
            print(f"Successfully processed: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            continue

    # Final analysis and output
    if all_results:
        # Results are already saved by the workflow
        if args.verbose:
            print(f"\nAll files processed successfully!")
            print(f"Results saved to: {args.output}")
        return all_results
    else:
        print("No files were successfully processed")
        return None


if __name__ == "__main__":
    # Run the workflow
    asyncio.run(main())
```


---

