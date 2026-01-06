# Plug-n-Play Instructions: UI Module (MCP-UI)

## Core Principles

1.  **Encapsulation**: This module manages its own state (Session Store) and logic (View Resolution), exposing only the MCP Tool surface.
2.  **Decoupling**: The Engine knows nothing about the specific rendering engine (React, Vue, CLI). It only outputs abstract Layout Trees.
3.  **Clear Interface**: The MCP Server is the *only* public API.

## Integration Steps

### 1. Installation

**Local Development (Editable Mode):**
```bash
cd ui-module
pip install -e .
```

**As a Dependency:**
Add to your `pyproject.toml` or `requirements.txt`:
```toml
dependencies = [
    "ui-module @ git+https://github.com/bannff/ui-module.git"
]
```

### 2. Configuration

The module is config-driven. Point it to a directory containing your view definitions.

**Directory Structure:**
```text
my-app-config/
├── settings.yaml      # Global theme/routing
└── views/
    ├── dashboard.yaml
    └── login.yaml
```

**Running the Server:**
```bash
# Via CLI
ui-module run --config-dir ./my-app-config

# Via Environment Variable
export UI_CONFIG_DIR=./my-app-config
ui-module run
```

### 3. Usage via MCP

Once running, any MCP Client (Claude Desktop, Cursor, Custom Agent) can use the tools.

**Render a View:**
```json
{
  "name": "render_view",
  "arguments": {
    "path": "/dashboard",
    "session_id": "user-session-123"
  }
}
```

**Handle an Event:**
```json
{
  "name": "handle_event",
  "arguments": {
    "event_id": "submit_login",
    "payload": { "username": "admin" },
    "session_id": "user-session-123"
  }
}
```

### 4. Authoring (Optional)

To enable the dangerous editing tools, set the environment variable:
```bash
export UI_ENABLE_AUTHORING_TOOLS=1
```
This enables `ui.authoring.upsert_view_definition` and others.

## Deployment

**Docker:**
```dockerfile
FROM python:3.10-slim
COPY . /app
RUN pip install /app
CMD ["ui-module", "run", "--config-dir", "/config"]
```

**AWS Lambda:**
Wrap the `mcp` server instance in a Lambda handler using `mcp-server-lambda` (future).
