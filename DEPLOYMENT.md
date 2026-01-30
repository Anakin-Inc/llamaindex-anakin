# Deployment Guide for llamaindex-anakin

This guide walks you through deploying your LlamaIndex Anakin workflows to production.

## Prerequisites

- Python 3.10 or higher
- `uv` package manager installed
- `llamactl` CLI tool installed
- Git repository
- Anakin API key
- (Optional) GitHub account for private repos

## Installation

### 1. Install Required Tools

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
export PATH="$HOME/.local/bin:$PATH"

# Install llamactl
uv tool install llamactl
```

### 2. Verify Installation

```bash
uv --version
llamactl --version
```

## Local Development

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd llamaindex-anakin
```

### 2. Set Up Environment

```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your API key
# ANAKIN_API_KEY=your-anakin-api-key-here
```

### 3. Install Dependencies

```bash
pip install -e .
```

### 4. Run Locally

```bash
llamactl serve
```

This starts a development server at `http://localhost:4501` with three workflow endpoints:

- **Scrape Workflow**: `POST /deployments/llamaindex-anakin/workflows/scrape/run`
- **Search Workflow**: `POST /deployments/llamaindex-anakin/workflows/search/run`
- **Agentic Search Workflow**: `POST /deployments/llamaindex-anakin/workflows/agentic-search/run`

### 5. Test the Workflows

```bash
# Test search workflow
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/search/run \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the latest AI trends?",
    "max_results": 5
  }'

# Test scrape workflow
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/scrape/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "country": "us"
  }'

# Test agentic search workflow
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/agentic-search/run \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Find pricing for top 5 CRM tools",
    "use_browser": true
  }'
```

## Deploying to LlamaCloud

### 1. Create a Git Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit"

# Add remote
git remote add origin https://github.com/your-org/llamaindex-anakin
# or for private repos:
# git remote add origin git@github.com:your-org/llamaindex-anakin.git

# Push to GitHub
git push -u origin main
```

### 2. Deploy to LlamaCloud

```bash
llamactl deployments create
```

This opens an interactive Terminal UI (TUI) where you can configure:

#### Required Fields

- **Name**: Human-readable deployment name (URL-safe)
  - Example: `llamaindex-anakin` or `anakin-workflows-prod`
  - This appears in your deployment URL

- **Git Repository**: Your repository URL
  - Public HTTP: `https://github.com/your-org/llamaindex-anakin`
  - Private GitHub: Install the GitHub app when prompted

- **Git Branch**: Branch to deploy from
  - Default: `main`
  - Can also be a tag or specific commit

- **Secrets**: Environment variables (pre-filled from `.env`)
  - `ANAKIN_API_KEY`: Your Anakin API key
  - Add any other required secrets

#### Optional Fields

- **Region**: Deployment region (auto-selected)
- **Resources**: CPU/Memory allocation (auto-configured)

### 3. Monitor Deployment

After creating the deployment, `llamactl` will show:

- Build logs in real-time
- Deployment status
- Access URLs

You can also monitor later with:

```bash
# View deployment details
llamactl deployments get

# View logs
llamactl deployments logs
```

### 4. Access Your Deployed Workflows

Your workflows will be accessible at:

```
https://<deployment-name>.llamacloud.ai/workflows/<workflow-name>/run
```

Example:

```
https://llamaindex-anakin.llamacloud.ai/workflows/search/run
```

## Updating Deployments

### 1. Update Your Code

```bash
# Make changes to your code
git add .
git commit -m "Update: ..."
git push origin main
```

### 2. Trigger Deployment Update

```bash
llamactl deployments update
```

This will:
- Pull latest code from your branch
- Rebuild the application
- Deploy with zero downtime

### 3. Update Secrets

```bash
llamactl deployments edit
```

Navigate to the Secrets section and update as needed.

## Environment Variables

### Required

- `ANAKIN_API_KEY`: Your Anakin API key from [anakin.io](https://anakin.io)

### Optional

- `ANAKIN_BASE_URL`: Custom Anakin API base URL (default: `https://api.anakin.io`)

## Deployment Configuration

All deployment configuration is in `pyproject.toml`:

```toml
[tool.llamadeploy]
env_files = [".env"]

[tool.llamadeploy.workflows]
scrape = "llamaindex_anakin.workflows.scrape_workflow:scrape_workflow"
search = "llamaindex_anakin.workflows.search_workflow:search_workflow"
agentic-search = "llamaindex_anakin.workflows.agentic_search_workflow:agentic_search_workflow"
```

### Adding New Workflows

1. Create a new workflow file in `src/llamaindex_anakin/workflows/`
2. Add entry to `[tool.llamadeploy.workflows]` in `pyproject.toml`
3. Commit and push
4. Run `llamactl deployments update`

## Continuous Deployment with GitHub Actions

You can automate deployments with GitHub Actions. See the [Continuous Deployment guide](https://developers.llamaindex.ai/python/llamaagents/llamactl/github-actions/) for details.

Example workflow (`.github/workflows/deploy.yml`):

```yaml
name: Deploy to LlamaCloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install llamactl
        run: |
          curl -LsSf https://astral.sh/uv/install.sh | sh
          export PATH="$HOME/.local/bin:$PATH"
          uv tool install llamactl
      
      - name: Deploy
        env:
          LLAMACTL_API_TOKEN: ${{ secrets.LLAMACTL_API_TOKEN }}
        run: llamactl deployments update
```

## Self-Hosting

You can also export workflows as Docker containers:

```bash
# Export to Docker
llamactl pkg export --format docker

# Build image
docker build -t llamaindex-anakin .

# Run container
docker run -p 4501:4501 \
  -e ANAKIN_API_KEY=your-api-key \
  llamaindex-anakin
```

## Monitoring and Logs

### View Deployment Status

```bash
llamactl deployments get
```

### Stream Logs

```bash
llamactl deployments logs --follow
```

### View Past Logs

```bash
llamactl deployments logs --since 1h
```

## Troubleshooting

### Build Failures

**Problem**: Deployment fails during build

**Solution**:
1. Check build logs: `llamactl deployments logs`
2. Verify `pyproject.toml` syntax
3. Ensure all dependencies are listed
4. Test locally first with `llamactl serve`

### Runtime Errors

**Problem**: Workflows fail at runtime

**Solution**:
1. Check runtime logs: `llamactl deployments logs`
2. Verify environment variables are set
3. Test API key is valid
4. Check API rate limits

### Connection Issues

**Problem**: Can't connect to deployed workflows

**Solution**:
1. Verify deployment is running: `llamactl deployments get`
2. Check URL is correct
3. Ensure firewall rules allow access
4. Check LlamaCloud status page

### Timeout Issues

**Problem**: Workflows timeout

**Solution**:
1. Increase timeout in workflow code
2. Check if operation genuinely needs more time
3. Optimize workflow logic
4. Consider breaking into smaller workflows

## Production Best Practices

### Security

- ✅ Never commit `.env` files or API keys
- ✅ Use environment variables for secrets
- ✅ Rotate API keys regularly
- ✅ Use private repositories for sensitive code
- ✅ Enable GitHub app for private repos

### Performance

- ✅ Set appropriate timeouts for operations
- ✅ Use caching when possible (`force_fresh=False`)
- ✅ Monitor API rate limits
- ✅ Implement retry logic for transient failures

### Reliability

- ✅ Implement comprehensive error handling
- ✅ Add health check endpoints
- ✅ Monitor deployment logs regularly
- ✅ Set up alerts for failures
- ✅ Test workflows before deploying

### Cost Optimization

- ✅ Use appropriate poll intervals (don't poll too frequently)
- ✅ Cache results when possible
- ✅ Set reasonable timeouts (don't wait indefinitely)
- ✅ Monitor API usage

## Support

Need help with deployment?

- 📚 [LlamaAgents Deployment Docs](https://developers.llamaindex.ai/python/llamaagents/llamactl/getting-started/)
- 💬 [LlamaIndex Discord](https://discord.gg/dGcwcsnxhU)
- 📧 Email: anakin@anakininc.com
- 🐛 [GitHub Issues](https://github.com/Anakin-Inc/llamaindex-anakin/issues)

---

Happy deploying! 🚀🦙
