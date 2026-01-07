# Architecture

## Overview

The UI Module follows the Engine/Interface separation pattern used across all modules.

```
src/ui_module/
├── engine/                    # Core business logic
│   ├── models.py             # Domain models
│   ├── registry.py           # Component registry
│   ├── view_manager.py       # Central orchestrator
│   ├── push_channel.py       # Real-time updates
│   ├── store/
│   │   └── view_store.py     # View persistence
│   └── adapters/
│       ├── base.py           # Adapter protocol
│       ├── json_adapter.py   # JSON output
│       └── mcpui_adapter.py  # MCP-UI output
└── server.py                 # MCP interface
```

## Core Components

### ViewManager

The central orchestrator that coordinates all operations:

```python
class ViewManager:
    def __init__(self):
        self.store = InMemoryViewStore()      # Persistence
        self.push_channel = PushChannel()      # Real-time
        self.registry = ComponentRegistry()    # Components
        self._adapters = {...}                 # Renderers
```

### ComponentRegistry

Manages available UI component types:

- Registers built-in components (text, chart, table, etc.)
- Stores JSON schemas for validation
- Applies default props when creating components
- Allows custom component registration

### ViewStore

Persists view state:

- `InMemoryViewStore` - Development/testing
- Future: `RedisViewStore` for production

### PushChannel

Manages real-time updates to connected clients:

- Client connection management
- View subscriptions (specific or wildcard)
- Async push to all subscribers
- Multiple channel types (callback, WebSocket, SSE)

### Adapters

Transform views into target formats:

- `JsonAdapter` - Raw JSON for custom frontends
- `McpUiAdapter` - MCP-UI UIResource for native clients

## Data Flow

### Creating a View

```
Agent → ui_create_view → ViewManager.create_view → ViewStore.save
```

### Adding a Component

```
Agent → ui_add_component
    → ViewManager.create_component (via Registry)
    → ViewManager.add_component
        → ViewStore.save
        → PushChannel.push → Connected Clients
```

### Rendering

```
Agent → ui_get_view(adapter="mcp-ui")
    → ViewManager.render
        → ViewStore.get
        → McpUiAdapter.render_view
    → UIResource returned to agent
```

## Models

### UIComponent

```python
@dataclass
class UIComponent:
    id: str
    component_type: ComponentType
    props: dict[str, Any]
    styles: dict[str, str]
    children: list[UIComponent]
    created_at: datetime
    updated_at: datetime
```

### UIView

```python
@dataclass
class UIView:
    id: str
    name: str
    components: list[UIComponent]
    layout: dict[str, Any]
    metadata: dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime
```

### ViewUpdate

```python
@dataclass
class ViewUpdate:
    view_id: str
    action: str  # "full", "add_component", "update_component", "remove_component"
    payload: dict[str, Any]
    version: int
    timestamp: datetime
```

## Extension Points

### Custom Adapters

```python
class SlackAdapter(RenderAdapter):
    @property
    def adapter_type(self) -> str:
        return "slack"
    
    def render_view(self, view: UIView) -> RenderResult:
        # Convert to Slack Block Kit
        blocks = self._view_to_blocks(view)
        return RenderResult(
            adapter_type="slack",
            content=blocks,
            content_type="application/json"
        )

manager.register_adapter(SlackAdapter())
```

### Custom Store

```python
class RedisViewStore:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url)
    
    def get(self, view_id: str) -> UIView | None:
        data = self.redis.get(f"view:{view_id}")
        return UIView.from_dict(json.loads(data)) if data else None
    
    def save(self, view: UIView) -> None:
        self.redis.set(f"view:{view.id}", json.dumps(view.to_dict()))
```
