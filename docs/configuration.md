# Configuration

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHORING_ENABLED` | `false` | Enable authoring tools (create, update, delete) |
| `LOG_LEVEL` | `INFO` | Logging level |

## Authoring Security

By default, authoring tools are disabled. This prevents unauthorized UI modifications.

To enable:

```bash
export AUTHORING_ENABLED=true
```

Or in MCP config:

```json
{
  "env": {
    "AUTHORING_ENABLED": "true"
  }
}
```

## Render Adapters

The module supports multiple render adapters:

### JSON Adapter (Default)

Outputs raw JSON for consumption by any frontend:

```python
result = manager.render(view_id, adapter_type="json")
# Returns: {"id": "...", "name": "...", "components": [...]}
```

### MCP-UI Adapter

Outputs MCP-UI `UIResource` objects for native client rendering:

```python
result = manager.render(view_id, adapter_type="mcp-ui")
# Returns: {"type": "inline_html", "content": "<div>...</div>"}
```

## Component Registry

### Built-in Components

| Type | Description | Key Props |
|------|-------------|----------|
| `text` | Text content | `content`, `variant` |
| `chart` | Data visualization | `chart_type`, `data`, `title` |
| `table` | Tabular data | `columns`, `rows` |
| `metric` | KPI display | `label`, `value`, `trend` |
| `card` | Container | `title`, `subtitle`, `content` |
| `alert` | Notification | `message`, `severity` |
| `progress` | Progress bar | `value`, `label`, `variant` |
| `form` | Input form | `fields`, `submit_label` |
| `button` | Action button | `label`, `variant` |
| `image` | Image display | `src`, `alt` |
| `list` | List items | `items`, `ordered` |

### Custom Components

Register custom component types:

```python
from ui_module.engine import ComponentRegistry, ComponentDefinition, ComponentType

registry = ComponentRegistry()
registry.register(ComponentDefinition(
    component_type=ComponentType.CUSTOM,
    name="MyWidget",
    description="A custom widget",
    schema={
        "type": "object",
        "properties": {
            "data": {"type": "object"}
        }
    },
    default_props={"theme": "dark"}
))
```

## Push Channel Configuration

The push channel supports multiple connection types:

- **Callback** - For in-process updates
- **WebSocket** - For real-time browser connections
- **SSE** - For server-sent events

```python
from ui_module.engine import PushChannel, ChannelType

channel = PushChannel()

# Callback connection
channel.connect(
    client_id="internal",
    channel_type=ChannelType.CALLBACK,
    callback=my_handler
)

# Subscribe to specific views or all (*)
channel.subscribe("internal", "dashboard-1")
channel.subscribe("internal", "*")  # All views
```
