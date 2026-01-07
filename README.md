# UI Module

[![CI](https://github.com/bannff/ui-module/actions/workflows/ci.yml/badge.svg)](https://github.com/bannff/ui-module/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/bannff/ui-module/branch/master/graph/badge.svg)](https://codecov.io/gh/bannff/ui-module)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

MCP-first Server-Driven UI Framework - a portable lego block for agent-driven user interfaces.

## Overview

The UI Module enables AI agents to create, manage, and update user interfaces through MCP tools. It supports two modes:

1. **JSON Adapter Mode** (works today): Agents author UI as JSON, which custom frontends render
2. **MCP-UI Mode** (future-ready): Native MCP client support when available

## Key Features

- **Component Registry**: 11 built-in component types (card, chart, form, table, etc.)
- **ViewManager**: Orchestrates view lifecycle and component composition
- **PushChannel**: Real-time WebSocket/SSE updates to connected frontends
- **MCP Resources**: Self-documenting component schemas and templates
- **MCP Prompts**: Guided workflows for common UI patterns
- **Context Envelope**: Cross-module composition with tenant/session tracking

## Installation

```bash
pip install -e .
```

## Quick Start

```bash
# Run the MCP server
ui-module run --config-dir ./config

# Or with Python
python -m ui_module --config-dir ./config
```

## MCP Tools

### Deterministic Tools (Query)
| Tool | Description |
|------|-------------|
| `ui_get_capabilities` | Returns module capabilities and feature flags |
| `ui_health_check` | Service health and connectivity status |
| `ui_describe_config_schema` | JSON schema for configuration |
| `ui_get_view_registry` | List all registered views |
| `ui_get_component_types` | Available component types |

### Operational Tools (Stateful)
| Tool | Description |
|------|-------------|
| `ui_create_view` | Create a new view with components |
| `ui_get_view` | Retrieve a view by ID |
| `ui_update_view` | Update view properties |
| `ui_delete_view` | Remove a view |
| `ui_add_component` | Add component to a view |
| `ui_update_component` | Update component properties |
| `ui_remove_component` | Remove component from view |
| `ui_render_view` | Render view for frontend consumption |
| `ui_push_update` | Push real-time update to clients |

### Authoring Tools (Admin)
| Tool | Description |
|------|-------------|
| `ui_authoring_get_status` | Authoring mode status |
| `ui_authoring_register_component` | Register custom component type |
| `ui_authoring_validate_view` | Validate view definition |

## MCP Resources

Resources provide self-documenting capabilities for agents:

| Resource URI | Description |
|--------------|-------------|
| `ui://components` | List all component types |
| `ui://components/{type}/schema` | JSON schema for component |
| `ui://templates` | Available UI templates |
| `ui://templates/{name}` | Specific template structure |
| `ui://views` | All registered views |
| `ui://views/{id}` | Specific view state |
| `ui://docs/getting-started` | Inline getting started guide |
| `ui://docs/best-practices` | Best practices documentation |

## MCP Prompts

Prompts guide agents toward effective UI creation:

| Prompt | Description |
|--------|-------------|
| `create_dashboard` | Multi-panel dashboard with metrics/charts |
| `add_visualization` | Add chart to existing view |
| `design_form` | Data entry form with validation |
| `update_metrics` | Update metric displays |
| `create_status_page` | System status monitoring page |

## Architecture

```
ui-module/
├── src/ui_module/
│   ├── engine/           # Core library (no MCP imports)
│   │   ├── models.py     # Pydantic models
│   │   ├── registry.py   # Component registry
│   │   ├── view_manager.py
│   │   ├── push_channel.py
│   │   ├── envelope.py   # Context envelope
│   │   ├── config.py     # Config loader
│   │   ├── runtime.py    # UIRuntime orchestrator
│   │   └── adapters/     # Render adapters
│   ├── server.py         # MCP server (interface)
│   ├── resources.py      # MCP resources
│   ├── prompts.py        # MCP prompts
│   └── cli.py            # CLI entrypoint
├── config/
│   ├── settings.yaml
│   └── views/            # View definitions
└── tests/
```

## Configuration

```yaml
# config/settings.yaml
ui:
  default_adapter: json
  enable_push: true
  push_transport: websocket
  
authoring:
  enabled: false  # Enable with UI_ENABLE_AUTHORING_TOOLS=1
  
components:
  custom_dir: ./config/components
```

## How It Works

1. **Agent creates view**: Calls `ui_create_view` with component structure
2. **Module stores view**: ViewManager persists and validates
3. **Frontend connects**: Via WebSocket or polling
4. **Agent renders**: Calls `ui_render_view` to get JSON
5. **Frontend displays**: Renders JSON as actual UI
6. **Agent updates**: Calls `ui_push_update` for real-time changes

The frontend is a "dumb renderer" - it doesn't need rebuilding when UI changes. The agent controls everything.

## Documentation

- [Getting Started](docs/getting-started.md)
- [Architecture](docs/architecture.md)
- [Configuration](docs/configuration.md)
- [Tools Reference](docs/tools-reference.md)
- [MCP Resources](docs/resources.md)
- [MCP Prompts](docs/prompts.md)
- [MCP-UI Integration](docs/mcpui-integration.md)
- [Steering Guide](STEERING.md)

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/ tests/
```

## License

MIT
