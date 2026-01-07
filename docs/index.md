# UI Module

Agent-driven UI management with real-time push updates.

## Overview

The UI Module enables AI agents to create and manipulate user interfaces in real-time. Instead of writing code to update a frontend, you simply tell the agent what you want to see, and it pushes the changes to your connected UI.

## Key Features

- **Component Registry** - Built-in UI primitives (charts, tables, metrics, forms, etc.)
- **View Management** - Create, update, and delete views
- **Real-time Push** - WebSocket/SSE updates to connected clients
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

## Quick Example

```python
# Agent creates a dashboard
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
```

Your connected frontend immediately displays the dashboard.

## Next Steps

- [Getting Started](getting-started.md) - Installation and setup
- [Configuration](configuration.md) - Environment and adapter configuration
- [Tools Reference](tools-reference.md) - Complete MCP tool documentation
- [Architecture](architecture.md) - Deep dive into the module design
