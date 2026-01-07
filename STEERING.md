# UI Module — Steering Document

This document defines the architectural principles, tool taxonomy, and governance rules for the UI Module.

## Architecture: Engine vs Interface

The module follows a strict separation between **Engine** (reusable library) and **Interface** (adapters).

### Engine (src/ui_module/engine/)

Pure business logic with no MCP or transport dependencies:

| File | Responsibility |
|------|----------------|
| `models.py` | Domain models (UIComponent, UIView, ViewUpdate) |
| `envelope.py` | Context envelope for cross-module composition |
| `config.py` | Configuration loading from config_dir |
| `registry.py` | Component type registry with schemas |
| `view_manager.py` | View/component orchestration |
| `push_channel.py` | Real-time update broadcasting |
| `runtime.py` | Module initialization and lifecycle |
| `store/` | Storage backends (memory, redis, filesystem) |
| `adapters/` | Render adapters (JSON, MCP-UI) |

### Interface (src/ui_module/server.py)

MCP server exposing engine capabilities:

- FastMCP tool definitions
- Request/response mapping
- No business logic

## Tool Taxonomy

MCP tools are categorized by their behavior and security requirements.

### A) Deterministic Tools (Safe, No Side Effects)

Always available, safe to call anytime:

| Tool | Description |
|------|-------------|
| `ui_get_capabilities` | Schema versions, adapters, feature flags |
| `ui_health_check` | Service status, connectivity, uptime |
| `ui_describe_config_schema` | JSON schema for configuration |
| `ui_get_view_registry` | Sanitized list of loaded views |
| `ui_get_component_registry` | Available component types |
| `ui_list_adapters` | Available render adapters |

### B) Operational Tools (Stateful, Auditable)

All accept a **context envelope** for cross-module composition:

```python
envelope = {
    "tenant_id": "...",        # Multi-tenancy
    "principal_id": "...",     # User/service identity
    "session_id": "...",       # Session tracking
    "request_id": "...",       # Request correlation
    "correlation_id": "...",   # Cross-module tracing
    "view_id": "...",          # UI-specific context
    "client_id": "...",        # Connected client
    "agent_id": "...",         # Agent identity
    "tool_name": "...",        # Tool being called
    "timestamp": "...",        # Request time
    "attributes": {}           # Custom attributes (validated)
}
```

| Tool | Description |
|------|-------------|
| `ui_list_views` | List all views |
| `ui_get_view` | Get view with adapter selection |
| `ui_get_push_channel_status` | Connected clients |
| `ui_get_view_history` | Update history |
| `ui_connect_client` | Register client |
| `ui_disconnect_client` | Disconnect client |
| `ui_subscribe` | Subscribe to view updates |

### C) Authoring Tools (Security-Gated)

Disabled by default. Require explicit opt-in:

```bash
export AUTHORING_ENABLED=true
# OR in config/settings.yaml:
# authoring_enabled: true
```

| Tool | Description |
|------|-------------|
| `ui_authoring_get_status` | Check authoring status |
| `ui_create_view` | Create new view |
| `ui_delete_view` | Delete view |
| `ui_add_component` | Add component to view |
| `ui_update_component` | Update component |
| `ui_remove_component` | Remove component |
| `ui_push_view` | Force push to clients |
| `ui_create_dashboard` | Create complete dashboard |

## Configuration (config_dir Pattern)

The module is config-driven with portable configuration:

```
config/
├── settings.yaml       # Module settings
└── views/              # View definitions
    ├── dashboard.yaml
    └── reports.yaml
```

### settings.yaml

```yaml
authoring_enabled: false
push_enabled: true
max_clients: 100
storage_backend: memory  # memory, redis, filesystem
default_adapter: json
enabled_adapters:
  - json
  - mcp-ui
max_views: 1000
max_components_per_view: 100
feature_flags:
  experimental_charts: false
```

### View Definition (views/*.yaml)

```yaml
id: sales-dashboard
name: Sales Dashboard
description: Real-time sales metrics
layout:
  type: grid
  columns: 3
components:
  - id: revenue-metric
    type: metric
    props:
      label: Revenue
      value: "$50,000"
      trend: up
  - id: sales-chart
    type: chart
    props:
      chart_type: line
      title: Monthly Sales
tags:
  - sales
  - dashboard
```

## Security Rules

### Authoring Tools

1. **Disabled by default** — Must explicitly enable via env var or config
2. **Path scoping** — Only allow operations within config_dir
3. **Traversal protection** — Validate all paths resolve within config_dir
4. **Schema validation** — Validate all inputs via Pydantic models
5. **No code execution** — Never execute user-provided code

### Transport Security

1. **stdio transport** — Do not log to stdout (reserved for MCP protocol)
2. **Redaction** — Never return secrets in registries or health checks
3. **Attribute limits** — Enforce size limits on envelope attributes

## Portability

### Stable Contracts

- MCP tool surface is the long-lived public API
- Internal interfaces ("ports") allow swappable backends
- Implementation can evolve without breaking consumers

### Backend Adapters

| Port | Default | Alternatives |
|------|---------|-------------|
| Storage | InMemoryViewStore | RedisViewStore, FilesystemViewStore |
| Render | JsonAdapter | McpUiAdapter, SlackAdapter |
| Push | Callback | WebSocket, SSE |

### No Cloud Lock-in

- Local-first defaults (memory storage, stdio transport)
- Cloud adapters (Redis, Lambda) are optional additions
- No hardcoded endpoints or credentials

## Cross-Module Composition

The context envelope enables clean composition with other modules:

```python
# Agent calls UI module with correlation context
result = await ui_add_component(
    view_id="dashboard",
    component_type="metric",
    props={"label": "Users", "value": 100},
    envelope={
        "tenant_id": "acme",
        "correlation_id": "trace-123",
        "agent_id": "sales-agent",
    }
)

# Same correlation_id can be used in telemetry, events, etc.
```

## Related Modules

- **telemetry-module** — Trace UI operations
- **events-module** — Emit UI events for subscribers
- **permissions-module** — Gate authoring by role
- **notification-module** — Notify on view changes
