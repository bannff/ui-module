# Tools Reference

## Query Tools

Always available, read-only operations.

### ui_list_views

List all available views.

```python
result = await call_tool("ui_list_views")
# Returns: {"views": [...], "total": 5}
```

### ui_get_view

Get a view by ID, optionally rendered through an adapter.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `view_id` | string | required | View ID |
| `adapter` | string | `"json"` | Render adapter (`"json"` or `"mcp-ui"`) |

```python
result = await call_tool("ui_get_view", {
    "view_id": "dashboard-1",
    "adapter": "mcp-ui"
})
```

### ui_get_component_registry

Get available component types and their schemas.

```python
result = await call_tool("ui_get_component_registry")
# Returns: {"components": [{"type": "text", "schema": {...}}, ...]}
```

### ui_get_push_channel_status

Get connected clients and subscriptions.

```python
result = await call_tool("ui_get_push_channel_status")
# Returns: {"connected_clients": 3, "clients": [...]}
```

### ui_list_adapters

List available render adapters.

```python
result = await call_tool("ui_list_adapters")
# Returns: {"adapters": ["json", "mcp-ui"], "default": "json"}
```

### ui_get_view_history

Get update history for views.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `view_id` | string | null | Filter by view ID |
| `limit` | int | 50 | Max updates to return |

---

## Authoring Tools

Require `AUTHORING_ENABLED=true`.

### ui_create_view

Create a new view.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | string | required | Display name |
| `view_id` | string | auto | Custom ID |
| `layout_type` | string | `"flex"` | `"flex"` or `"grid"` |
| `layout_columns` | int | 1 | Grid columns |

```python
result = await call_tool("ui_create_view", {
    "name": "Sales Dashboard",
    "layout_type": "grid",
    "layout_columns": 3
})
```

### ui_delete_view

Delete a view.

| Parameter | Type | Description |
|-----------|------|-------------|
| `view_id` | string | View to delete |

### ui_add_component

Add a component to a view.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `view_id` | string | required | Target view |
| `component_type` | string | required | Component type |
| `props` | object | {} | Component properties |
| `styles` | object | {} | CSS styles |
| `component_id` | string | auto | Custom ID |
| `position` | int | null | Insert position |

```python
await call_tool("ui_add_component", {
    "view_id": "dashboard-1",
    "component_type": "metric",
    "props": {
        "label": "Revenue",
        "value": "$50,000",
        "trend": "up",
        "trend_value": "+15%"
    }
})
```

### ui_update_component

Update a component's properties or styles.

| Parameter | Type | Description |
|-----------|------|-------------|
| `view_id` | string | View containing component |
| `component_id` | string | Component to update |
| `props` | object | Properties to merge |
| `styles` | object | Styles to merge |

```python
await call_tool("ui_update_component", {
    "view_id": "dashboard-1",
    "component_id": "metric-1",
    "props": {"value": "$55,000"}
})
```

### ui_remove_component

Remove a component from a view.

| Parameter | Type | Description |
|-----------|------|-------------|
| `view_id` | string | View containing component |
| `component_id` | string | Component to remove |

### ui_push_view

Force push full view state to all subscribers.

| Parameter | Type | Description |
|-----------|------|-------------|
| `view_id` | string | View to push |

### ui_create_dashboard

Convenience tool to create a complete dashboard.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | string | Dashboard name |
| `metrics` | array | Metric configs |
| `charts` | array | Chart configs |
| `tables` | array | Table configs |

```python
await call_tool("ui_create_dashboard", {
    "name": "Executive Dashboard",
    "metrics": [
        {"label": "Revenue", "value": "$1.2M", "trend": "up"},
        {"label": "Customers", "value": "5,432", "trend": "up"}
    ],
    "charts": [
        {"title": "Monthly Trend", "chart_type": "line", "data": [...]}
    ]
})
```

---

## Client Connection Tools

### ui_connect_client

Register a client for receiving updates.

| Parameter | Type | Description |
|-----------|------|-------------|
| `client_id` | string | Unique client ID |
| `subscribe_to` | array | View IDs to subscribe (use `"*"` for all) |

### ui_disconnect_client

Disconnect a client.

| Parameter | Type | Description |
|-----------|------|-------------|
| `client_id` | string | Client to disconnect |

### ui_subscribe

Subscribe a client to view updates.

| Parameter | Type | Description |
|-----------|------|-------------|
| `client_id` | string | Client ID |
| `view_id` | string | View to subscribe (use `"*"` for all) |
