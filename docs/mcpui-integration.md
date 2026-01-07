# MCP-UI Integration

## What is MCP-UI?

MCP-UI is a protocol extension that allows MCP servers to return rich, interactive UI components that MCP clients can render natively within the chat interface.

See: [mcpui.dev](https://mcpui.dev/)

## Current Status

⚠️ **MCP-UI client support is limited.** Most MCP clients (Claude Desktop, Cursor, etc.) don't yet support rendering UIResource objects. The MCP-UI adapter is included for future compatibility.

## How It Works

The `McpUiAdapter` converts your views into MCP-UI `UIResource` objects:

```python
# Your view
view = UIView(
    id="dashboard",
    name="Sales Dashboard",
    components=[
        UIComponent(type=METRIC, props={"label": "Revenue", "value": "$50K"})
    ]
)

# Rendered as MCP-UI
result = manager.render("dashboard", adapter_type="mcp-ui")
# Returns:
# {
#   "type": "inline_html",
#   "content": "<div class='mcp-ui-view'>...<div class='mcp-ui-metric'>...</div>...</div>",
#   "metadata": {"view_id": "dashboard", "version": 1}
# }
```

## UIResource Types

The adapter supports:

| Type | Description |
|------|-------------|
| `inline_html` | HTML string rendered inline (default) |
| `external_url` | URL to external page (future) |
| `remote_dom` | Remote DOM script (future) |

## Using the MCP-UI Adapter

### Via MCP Tool

```python
result = await call_tool("ui_get_view", {
    "view_id": "dashboard",
    "adapter": "mcp-ui"
})
```

### Programmatically

```python
from ui_module.engine import ViewManager, McpUiAdapter
from ui_module.engine.adapters.mcpui_adapter import UIResourceType

manager = ViewManager()

# Use default inline HTML
result = manager.render("dashboard", adapter_type="mcp-ui")

# Or configure the adapter
custom_adapter = McpUiAdapter(resource_type=UIResourceType.INLINE_HTML)
manager.register_adapter(custom_adapter)
```

## Component Rendering

Each component type has an HTML renderer:

| Component | HTML Output |
|-----------|-------------|
| `text` | `<p>`, `<h1>`, etc. based on variant |
| `metric` | Styled metric card with trend indicator |
| `chart` | Placeholder with embedded JSON data |
| `table` | Standard HTML table |
| `alert` | Styled alert box with severity colors |
| `progress` | Linear or circular progress indicator |
| `form` | HTML form with inputs |

## Styling

The adapter includes embedded CSS for consistent styling:

```css
.mcp-ui-view { font-family: system-ui, sans-serif; }
.mcp-ui-metric .metric-value { font-size: 2rem; font-weight: bold; }
.mcp-ui-alert--error { background: #fee2e2; color: #991b1b; }
/* ... */
```

## Future Compatibility

When MCP clients add UIResource support:

1. Your existing views will "just work"
2. Agents can request `adapter="mcp-ui"` to get native rendering
3. No code changes needed on your side

## Hybrid Approach

Until MCP-UI is widely supported, use both:

1. **JSON adapter** → Your custom frontend (works today)
2. **MCP-UI adapter** → Native client rendering (future)

```python
# For your frontend
json_result = manager.render(view_id, adapter_type="json")
push_to_frontend(json_result.content)

# For MCP client (when supported)
mcpui_result = manager.render(view_id, adapter_type="mcp-ui")
return mcpui_result.content  # UIResource
```
