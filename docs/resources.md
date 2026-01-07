# MCP Resources

MCP Resources provide a way for agents to discover and understand the UI module's capabilities without making tool calls. Resources are read-only data that agents can access to learn about available components, templates, and documentation.

## Overview

Resources help agents:

- **Discover** what UI components are available
- **Understand** component schemas and properties
- **Access** pre-built templates for common patterns
- **Read** documentation inline

## Available Resources

### Component Resources

#### `ui://components`

Returns a list of all registered component types with their metadata.

```json
{
  "components": [
    {
      "type": "card",
      "category": "container",
      "description": "A container with optional header, content, and actions"
    },
    {
      "type": "chart",
      "category": "visualization",
      "description": "Data visualization component supporting multiple chart types"
    }
  ]
}
```

#### `ui://components/{type}/schema`

Returns the JSON schema for a specific component type.

```json
{
  "type": "object",
  "properties": {
    "title": {"type": "string"},
    "subtitle": {"type": "string"},
    "content": {"type": "object"},
    "actions": {"type": "array"}
  },
  "required": ["title"]
}
```

### Template Resources

#### `ui://templates`

Returns available UI templates for common patterns.

```json
{
  "templates": [
    {
      "name": "dashboard",
      "description": "Multi-panel dashboard with metrics and charts",
      "components": ["grid", "card", "chart", "metric"]
    },
    {
      "name": "form",
      "description": "Data entry form with validation",
      "components": ["form", "input", "select", "button"]
    }
  ]
}
```

#### `ui://templates/{name}`

Returns a specific template with its full structure.

### View Resources

#### `ui://views`

Returns all registered views in the system.

#### `ui://views/{view_id}`

Returns a specific view's current state and structure.

### Documentation Resources

#### `ui://docs/getting-started`

Inline getting started guide for agents.

#### `ui://docs/best-practices`

Best practices for UI composition.

## Usage in Agents

Agents can read resources to understand capabilities before making tool calls:

```python
# Agent workflow example

# 1. Discover available components
components = await read_resource("ui://components")

# 2. Get schema for a specific component
card_schema = await read_resource("ui://components/card/schema")

# 3. Find a suitable template
templates = await read_resource("ui://templates")

# 4. Now make informed tool calls
await call_tool("ui_create_view", {
    "view_id": "my-dashboard",
    "template": "dashboard"
})
```

## Benefits

1. **Self-Discovery**: Agents can explore capabilities without documentation
2. **Schema Validation**: Agents can validate their payloads before sending
3. **Template Guidance**: Pre-built patterns reduce errors
4. **Reduced Errors**: Understanding schemas prevents malformed requests
