# UI Module

A Model Context Protocol (MCP) server for agent-driven UI management with real-time push updates. Talk to an agent, and it updates your frontend in real-time.

## Features

- **Component Registry** - Built-in UI primitives (charts, tables, metrics, forms, etc.)
- **View Management** - Create, update, and delete views via MCP tools
- **Real-time Push** - WebSocket/SSE updates to connected frontends
- **Multiple Adapters** - JSON for custom frontends, MCP-UI for native client support
- **Security-Gated Authoring** - Protected tools for UI manipulation

## How It Works

```
┌─────────────────┐     MCP      ┌──────────────┐     WebSocket     ┌─────────────┐
│  MCP Client     │ ──────────►  │  ui-module   │  ───────────────► │  Your App   │
│  (Claude, etc)  │              │  (MCP Server)│                   │  (React/Web)│
└─────────────────┘              └──────────────┘                   └─────────────┘
```

1. You talk to an agent in your MCP client
2. Agent calls UI module tools to create/update views
3. UI module pushes updates to your connected frontend
4. Your frontend renders the changes in real-time

## Architecture

```
src/ui_module/
├── engine/                    # Core business logic
│   ├── models.py             # UIComponent, UIView, ViewUpdate
│   ├── registry.py           # ComponentRegistry with built-in types
│   ├── view_manager.py       # Central orchestrator
│   ├── push_channel.py       # Real-time client updates
│   ├── store/
│   │   └── view_store.py     # View persistence
│   └── adapters/
│       ├── json_adapter.py   # JSON output for custom frontends
│       └── mcpui_adapter.py  # MCP-UI protocol support
└── server.py                 # MCP server with tool definitions
```

## Installation

```bash
# Clone the repository
git clone https://github.com/bannff/ui-module.git
cd ui-module

# Install dependencies
uv sync
```

## Configuration

### Environment Variables

```bash
AUTHORING_ENABLED=true    # Enable authoring tools
```

### MCP Configuration

```json
{
  "mcpServers": {
    "ui": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ui-module", "python", "-m", "ui_module.server"],
      "env": {
        "AUTHORING_ENABLED": "true"
      }
    }
  }
}
```

## MCP Tools

### Query Tools

| Tool | Description |
|------|-------------|
| `ui_list_views` | List all available views |
| `ui_get_view` | Get a view (JSON or MCP-UI format) |
| `ui_get_component_registry` | Get available component types |
| `ui_get_push_channel_status` | Get connected clients |
| `ui_list_adapters` | List render adapters |
| `ui_get_view_history` | Get update history |

### Authoring Tools (Security-Gated)

| Tool | Description |
|------|-------------|
| `ui_create_view` | Create a new view |
| `ui_delete_view` | Delete a view |
| `ui_add_component` | Add component to view |
| `ui_update_component` | Update component props/styles |
| `ui_remove_component` | Remove component from view |
| `ui_push_view` | Force push view to clients |
| `ui_create_dashboard` | Create complete dashboard |

### Client Connection Tools

| Tool | Description |
|------|-------------|
| `ui_connect_client` | Register client for updates |
| `ui_disconnect_client` | Disconnect a client |
| `ui_subscribe` | Subscribe to view updates |

## Usage Example

```python
# Create a dashboard with metrics and charts
await call_tool("ui_create_dashboard", {
    "name": "Sales Dashboard",
    "metrics": [
        {"label": "Revenue", "value": "$50,000", "trend": "up"},
        {"label": "Orders", "value": "1,234", "trend": "up"},
    ],
    "charts": [
        {"title": "Sales by Region", "chart_type": "bar", "data": [...]}
    ]
})

# Update a metric value
await call_tool("ui_update_component", {
    "view_id": "dashboard-1",
    "component_id": "metric-revenue",
    "props": {"value": "$55,000"}
})
```

## Component Types

| Type | Description |
|------|-------------|
| `text` | Text with variants (h1, h2, body, etc.) |
| `chart` | Line, bar, pie, area charts |
| `table` | Sortable/filterable tables |
| `metric` | KPI cards with trends |
| `card` | Container cards |
| `alert` | Info/success/warning/error alerts |
| `progress` | Linear/circular progress |
| `form` | Input forms |
| `button` | Action buttons |
| `image` | Images |
| `list` | Ordered/unordered lists |

## MCP-UI Support

The module includes an MCP-UI adapter for future native client rendering:

```python
# Get view as MCP-UI UIResource
result = await call_tool("ui_get_view", {
    "view_id": "dashboard",
    "adapter": "mcp-ui"
})
# Returns UIResource with inline HTML
```

See [MCP-UI Integration](docs/mcpui-integration.md) for details.

## Testing

```bash
uv run pytest
```

## Documentation

```bash
uv run mkdocs serve
```

## Related Modules

- [telemetry-module](https://github.com/bannff/telemetry-module) - OpenTelemetry integration
- [notification-module](https://github.com/bannff/notification-module) - Multi-channel notifications
- [permissions-module](https://github.com/bannff/permissions-module) - RBAC and audit logging
- [events-module](https://github.com/bannff/events-module) - Event bus with subscriptions
- [knowledge-base-module](https://github.com/bannff/knowledge-base-module) - Vector search with ChromaDB
- [backend-module](https://github.com/bannff/backend-module) - Database adapter registry
- [blockchain-module](https://github.com/bannff/blockchain-module) - Blockchain/DLT integration
- [payments-module](https://github.com/bannff/payments-module) - Payment processing

## License

MIT License - see [LICENSE](LICENSE) for details.
