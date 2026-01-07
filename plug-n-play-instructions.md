# Plug-n-Play Instructions

This document explains how to integrate the UI Module into your project.

## Quick Start

### 1. Install the Module

```bash
# Clone the repository
git clone https://github.com/bannff/ui-module.git
cd ui-module

# Install with uv
uv sync

# Or with pip
pip install -e .
```

### 2. Configure MCP Client

Add to your MCP client configuration (e.g., Claude Desktop, Cursor):

```json
{
  "mcpServers": {
    "ui": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/ui-module", "python", "-m", "ui_module.server"],
      "env": {
        "UI_CONFIG_DIR": "/path/to/ui-module/config",
        "AUTHORING_ENABLED": "true"
      }
    }
  }
}
```

### 3. Verify Installation

Test the module is working:

```python
# Call the capabilities tool
result = await call_tool("ui_get_capabilities")
print(result)
# Should show: {"module": "ui-module", "version": "0.2.0", ...}

# Check health
health = await call_tool("ui_health_check")
print(health)
# Should show: {"status": "healthy", ...}
```

## Configuration

### Config Directory Structure

```
config/
├── settings.yaml       # Module settings
└── views/              # Pre-defined view templates
    ├── dashboard.yaml
    └── reports.yaml
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UI_CONFIG_DIR` | `./config` | Path to configuration directory |
| `AUTHORING_ENABLED` | `false` | Enable authoring tools |

### settings.yaml

```yaml
# Enable authoring tools (can also use env var)
authoring_enabled: false

# Push channel settings
push_enabled: true
max_clients: 100

# Storage backend
storage_backend: memory  # memory, redis, filesystem

# Render adapters
default_adapter: json
enabled_adapters:
  - json
  - mcp-ui

# Limits
max_views: 1000
max_components_per_view: 100
```

## Tool Categories

### Deterministic Tools (Always Available)

| Tool | Description |
|------|-------------|
| `ui_get_capabilities` | Module version, features, adapters |
| `ui_health_check` | Service health status |
| `ui_describe_config_schema` | JSON schema for configuration |
| `ui_get_view_registry` | List of loaded views |
| `ui_get_component_registry` | Available component types |
| `ui_list_adapters` | Available render adapters |

### Operational Tools (With Context Envelope)

All operational tools accept an optional `envelope` parameter for correlation:

```python
await call_tool("ui_list_views", {
    "envelope": {
        "tenant_id": "acme",
        "correlation_id": "trace-123"
    }
})
```

| Tool | Description |
|------|-------------|
| `ui_list_views` | List all views |
| `ui_get_view` | Get view with adapter selection |
| `ui_get_push_channel_status` | Connected clients |
| `ui_get_view_history` | Update history |
| `ui_connect_client` | Register client for updates |
| `ui_disconnect_client` | Disconnect client |
| `ui_subscribe` | Subscribe to view updates |

### Authoring Tools (Require AUTHORING_ENABLED=true)

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

## Frontend Integration

The UI module pushes updates to connected frontends. Here's how to integrate:

### 1. Connect Your Frontend

```javascript
// Register as a client
const response = await mcpClient.callTool('ui_connect_client', {
  client_id: 'my-frontend',
  subscribe_to: ['*']  // Subscribe to all views
});
```

### 2. Listen for Updates

```javascript
// Poll for updates or use WebSocket
const ws = new WebSocket('ws://localhost:8080/ui/updates');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  
  switch (update.action) {
    case 'full':
      setView(update.payload);
      break;
    case 'add_component':
      addComponent(update.payload.component);
      break;
    case 'update_component':
      updateComponent(update.payload);
      break;
    case 'remove_component':
      removeComponent(update.payload.component_id);
      break;
  }
};
```

### 3. Render Components

```jsx
function ComponentRenderer({ component }) {
  switch (component.type) {
    case 'text':
      return <Text {...component.props} />;
    case 'metric':
      return <MetricCard {...component.props} />;
    case 'chart':
      return <Chart {...component.props} />;
    case 'table':
      return <DataTable {...component.props} />;
    default:
      return <div>Unknown: {component.type}</div>;
  }
}
```

## Cross-Module Composition

Use the context envelope to correlate operations across modules:

```python
# Create a dashboard with correlation context
envelope = {
    "tenant_id": "acme",
    "correlation_id": "user-session-123",
    "agent_id": "sales-agent"
}

# UI module
await call_tool("ui_create_dashboard", {
    "name": "Sales Dashboard",
    "metrics": [...],
    "envelope": envelope
})

# Telemetry module (same correlation_id)
await call_tool("telemetry_emit_event", {
    "event": "dashboard_created",
    "envelope": envelope
})

# Events module (same correlation_id)
await call_tool("events_publish", {
    "topic": "ui.dashboard.created",
    "envelope": envelope
})
```

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/ui_module

# Run specific test file
uv run pytest tests/test_runtime.py -v
```

## Troubleshooting

### Authoring tools return "disabled" error

Set the environment variable:
```bash
export AUTHORING_ENABLED=true
```

Or in config/settings.yaml:
```yaml
authoring_enabled: true
```

### Views not loading from config

Check that `UI_CONFIG_DIR` points to a directory with:
- `settings.yaml`
- `views/*.yaml`

### Health check shows "unhealthy"

Check the `last_error` field in the health check response for details.
