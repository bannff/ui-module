# Getting Started

## Installation

```bash
# Clone the repository
git clone https://github.com/bannff/ui-module.git
cd ui-module

# Install dependencies
uv sync
```

## MCP Configuration

Add to your MCP client configuration:

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

## Basic Usage

### 1. Create a View

```python
# Via MCP tool
result = await call_tool("ui_create_view", {
    "name": "My Dashboard",
    "layout_type": "grid",
    "layout_columns": 3
})
view_id = result["view"]["id"]
```

### 2. Add Components

```python
# Add a metric
await call_tool("ui_add_component", {
    "view_id": view_id,
    "component_type": "metric",
    "props": {
        "label": "Total Users",
        "value": 1234,
        "trend": "up",
        "trend_value": "+12%"
    }
})

# Add a chart
await call_tool("ui_add_component", {
    "view_id": view_id,
    "component_type": "chart",
    "props": {
        "chart_type": "line",
        "title": "User Growth",
        "data": [{"month": "Jan", "users": 100}, {"month": "Feb", "users": 150}]
    }
})
```

### 3. Connect a Frontend

Your frontend connects to receive updates:

```javascript
// React example
const [view, setView] = useState(null);

useEffect(() => {
  // Connect to UI module
  const ws = new WebSocket('ws://localhost:8080/ui');
  
  ws.onmessage = (event) => {
    const update = JSON.parse(event.data);
    if (update.action === 'full') {
      setView(update.payload);
    } else if (update.action === 'add_component') {
      setView(prev => ({
        ...prev,
        components: [...prev.components, update.payload.component]
      }));
    }
  };
  
  return () => ws.close();
}, []);
```

### 4. Render Components

```jsx
function ViewRenderer({ view }) {
  return (
    <div className="view" style={layoutToStyle(view.layout)}>
      {view.components.map(component => (
        <ComponentRenderer key={component.id} component={component} />
      ))}
    </div>
  );
}

function ComponentRenderer({ component }) {
  switch (component.type) {
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

## Running Tests

```bash
uv run pytest
```

## Next Steps

- See [Tools Reference](tools-reference.md) for all available tools
- See [Architecture](architecture.md) for design details
- See [MCP-UI Integration](mcpui-integration.md) for native client support
