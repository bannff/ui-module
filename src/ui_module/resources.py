"""MCP Resources for UI Module.

Resources provide read-only data that helps agents understand
what's available and how to use the module effectively.
"""

import json
from typing import Any


def get_component_schema_resource(component_type: str, registry) -> dict[str, Any]:
    """Get schema resource for a component type."""
    from .engine.models import ComponentType

    try:
        comp_type = ComponentType(component_type)
        definition = registry.get(comp_type)
        if definition:
            return {
                "uri": f"ui://components/{component_type}",
                "name": f"{definition.name} Component Schema",
                "description": definition.description,
                "mimeType": "application/json",
                "content": json.dumps(
                    {
                        "type": component_type,
                        "name": definition.name,
                        "description": definition.description,
                        "schema": definition.schema,
                        "default_props": definition.default_props,
                        "default_styles": definition.default_styles,
                        "example": _get_component_example(component_type),
                    },
                    indent=2,
                ),
            }
    except ValueError:
        pass

    return {
        "uri": f"ui://components/{component_type}",
        "name": f"Unknown Component: {component_type}",
        "mimeType": "application/json",
        "content": json.dumps({"error": f"Unknown component type: {component_type}"}),
    }


def get_all_components_resource(registry) -> dict[str, Any]:
    """Get resource listing all available components."""
    components = []
    for defn in registry.list_components():
        components.append(
            {
                "type": defn.component_type.value,
                "name": defn.name,
                "description": defn.description,
                "schema": defn.schema,
            }
        )

    return {
        "uri": "ui://components",
        "name": "All UI Components",
        "description": "Complete list of available UI component types with their schemas",
        "mimeType": "application/json",
        "content": json.dumps(
            {
                "components": components,
                "total": len(components),
            },
            indent=2,
        ),
    }


def get_template_resource(template_name: str) -> dict[str, Any]:
    """Get a view template resource."""
    templates = _get_templates()

    if template_name in templates:
        template = templates[template_name]
        return {
            "uri": f"ui://templates/{template_name}",
            "name": template["name"],
            "description": template["description"],
            "mimeType": "application/json",
            "content": json.dumps(template, indent=2),
        }

    return {
        "uri": f"ui://templates/{template_name}",
        "name": f"Unknown Template: {template_name}",
        "mimeType": "application/json",
        "content": json.dumps({"error": f"Unknown template: {template_name}"}),
    }


def get_all_templates_resource() -> dict[str, Any]:
    """Get resource listing all available templates."""
    templates = _get_templates()

    return {
        "uri": "ui://templates",
        "name": "View Templates",
        "description": "Pre-built view templates for common UI patterns",
        "mimeType": "application/json",
        "content": json.dumps(
            {
                "templates": list(templates.keys()),
                "details": {
                    k: {"name": v["name"], "description": v["description"]}
                    for k, v in templates.items()
                },
            },
            indent=2,
        ),
    }


def get_view_resource(view_id: str, view_manager) -> dict[str, Any]:
    """Get a specific view as a resource."""
    view = view_manager.get_view(view_id)

    if view:
        return {
            "uri": f"ui://views/{view_id}",
            "name": view.name,
            "description": f"View: {view.name} (v{view.version})",
            "mimeType": "application/json",
            "content": json.dumps(view.to_dict(), indent=2),
        }

    return {
        "uri": f"ui://views/{view_id}",
        "name": f"Unknown View: {view_id}",
        "mimeType": "application/json",
        "content": json.dumps({"error": f"View not found: {view_id}"}),
    }


def get_docs_resource(doc_name: str) -> dict[str, Any]:
    """Get documentation resource."""
    docs = _get_docs()

    if doc_name in docs:
        doc = docs[doc_name]
        return {
            "uri": f"ui://docs/{doc_name}",
            "name": doc["name"],
            "description": doc["description"],
            "mimeType": "text/markdown",
            "content": doc["content"],
        }

    return {
        "uri": f"ui://docs/{doc_name}",
        "name": f"Unknown Doc: {doc_name}",
        "mimeType": "text/plain",
        "content": f"Documentation not found: {doc_name}",
    }


def list_all_resources(registry, view_manager) -> list[dict[str, Any]]:
    """List all available resources."""
    resources = []

    # Component schemas
    resources.append(
        {
            "uri": "ui://components",
            "name": "All UI Components",
            "description": "Complete list of available UI component types",
            "mimeType": "application/json",
        }
    )

    for defn in registry.list_components():
        resources.append(
            {
                "uri": f"ui://components/{defn.component_type.value}",
                "name": f"{defn.name} Schema",
                "description": defn.description,
                "mimeType": "application/json",
            }
        )

    # Templates
    resources.append(
        {
            "uri": "ui://templates",
            "name": "View Templates",
            "description": "Pre-built view templates",
            "mimeType": "application/json",
        }
    )

    for name, template in _get_templates().items():
        resources.append(
            {
                "uri": f"ui://templates/{name}",
                "name": template["name"],
                "description": template["description"],
                "mimeType": "application/json",
            }
        )

    # Current views
    for view in view_manager.list_views():
        resources.append(
            {
                "uri": f"ui://views/{view.id}",
                "name": view.name,
                "description": f"View with {len(view.components)} components",
                "mimeType": "application/json",
            }
        )

    # Documentation
    for name, doc in _get_docs().items():
        resources.append(
            {
                "uri": f"ui://docs/{name}",
                "name": doc["name"],
                "description": doc["description"],
                "mimeType": "text/markdown",
            }
        )

    # External resources
    resources.append(
        {
            "uri": "https://mcpui.dev/guide/introduction",
            "name": "MCP-UI Documentation",
            "description": "Official MCP-UI protocol documentation",
            "mimeType": "text/html",
        }
    )

    return resources


def _get_component_example(component_type: str) -> dict[str, Any]:
    """Get example usage for a component type."""
    examples = {
        "text": {
            "props": {"content": "Hello, World!", "variant": "h1"},
            "description": "Display a heading",
        },
        "metric": {
            "props": {"label": "Revenue", "value": "$50,000", "trend": "up", "trend_value": "+12%"},
            "description": "Display a KPI with trend indicator",
        },
        "chart": {
            "props": {
                "chart_type": "line",
                "title": "Monthly Sales",
                "data": [{"month": "Jan", "value": 100}, {"month": "Feb", "value": 150}],
            },
            "description": "Display a line chart",
        },
        "table": {
            "props": {
                "columns": [{"key": "name", "label": "Name"}, {"key": "value", "label": "Value"}],
                "rows": [{"name": "Item 1", "value": 100}, {"name": "Item 2", "value": 200}],
            },
            "description": "Display tabular data",
        },
        "alert": {
            "props": {"message": "Operation successful!", "severity": "success"},
            "description": "Display a success alert",
        },
        "progress": {
            "props": {"value": 75, "label": "Loading..."},
            "description": "Display a progress bar",
        },
        "card": {
            "props": {
                "title": "Card Title",
                "subtitle": "Subtitle",
                "content": "Card content here",
            },
            "description": "Display a card container",
        },
        "form": {
            "props": {
                "fields": [
                    {"name": "email", "type": "email", "label": "Email"},
                    {"name": "message", "type": "textarea", "label": "Message"},
                ],
                "submit_label": "Send",
            },
            "description": "Display a form",
        },
    }
    return examples.get(component_type, {"props": {}, "description": "No example available"})


def _get_templates() -> dict[str, dict[str, Any]]:
    """Get pre-built view templates."""
    return {
        "dashboard": {
            "name": "Dashboard Template",
            "description": "A standard dashboard with metrics, charts, and tables",
            "layout": {"type": "grid", "columns": 3},
            "suggested_components": [
                {"type": "metric", "count": "3-6", "purpose": "KPIs at the top"},
                {"type": "chart", "count": "1-3", "purpose": "Data visualizations"},
                {"type": "table", "count": "0-2", "purpose": "Detailed data"},
            ],
            "example": {
                "name": "Sales Dashboard",
                "metrics": [
                    {"label": "Revenue", "value": "$50K"},
                    {"label": "Orders", "value": "1,234"},
                    {"label": "Customers", "value": "567"},
                ],
                "charts": [{"title": "Monthly Trend", "chart_type": "line"}],
            },
        },
        "report": {
            "name": "Report Template",
            "description": "A report layout with title, summary, and detailed sections",
            "layout": {"type": "flex", "direction": "column"},
            "suggested_components": [
                {"type": "text", "variant": "h1", "purpose": "Report title"},
                {"type": "text", "variant": "body", "purpose": "Executive summary"},
                {"type": "chart", "count": "1-2", "purpose": "Key visualizations"},
                {"type": "table", "count": "1-3", "purpose": "Detailed data tables"},
            ],
        },
        "form": {
            "name": "Form Template",
            "description": "A form layout for data collection",
            "layout": {"type": "flex", "direction": "column"},
            "suggested_components": [
                {"type": "text", "variant": "h2", "purpose": "Form title"},
                {"type": "form", "count": 1, "purpose": "Input fields"},
                {"type": "alert", "purpose": "Validation messages"},
            ],
        },
        "status": {
            "name": "Status Page Template",
            "description": "A status/health page showing system state",
            "layout": {"type": "grid", "columns": 2},
            "suggested_components": [
                {"type": "text", "variant": "h1", "purpose": "Page title"},
                {"type": "alert", "count": "1-3", "purpose": "Status indicators"},
                {"type": "metric", "count": "2-6", "purpose": "Health metrics"},
                {"type": "progress", "count": "0-4", "purpose": "Resource usage"},
            ],
        },
    }


def _get_docs() -> dict[str, dict[str, Any]]:
    """Get documentation content."""
    return {
        "getting-started": {
            "name": "Getting Started",
            "description": "Quick start guide for using the UI module",
            "content": """# Getting Started with UI Module

## Overview

The UI Module lets you create and update user interfaces through conversation.
Instead of writing code, you describe what you want and the agent builds it.

## Basic Workflow

1. **Create a view**: `ui_create_view(name="My Dashboard")`
2. **Add components**: `ui_add_component(view_id, component_type="metric", props={...})`
3. **Update as needed**: `ui_update_component(view_id, component_id, props={...})`

## Available Components

- `text` - Headings and paragraphs
- `metric` - KPI cards with trends
- `chart` - Line, bar, pie charts
- `table` - Data tables
- `alert` - Notifications
- `progress` - Progress bars
- `form` - Input forms
- `card` - Container cards

## Tips

- Use `ui://components` resource to see all component schemas
- Use `ui://templates/dashboard` for dashboard patterns
- Always provide meaningful labels and titles
""",
        },
        "component-guide": {
            "name": "Component Guide",
            "description": "Detailed guide for each component type",
            "content": """# Component Guide

## Metric Component

Best for: KPIs, statistics, single values with context

```json
{
  "type": "metric",
  "props": {
    "label": "Revenue",
    "value": "$50,000",
    "unit": "USD",
    "trend": "up",
    "trend_value": "+12%"
  }
}
```

## Chart Component

Best for: Trends, comparisons, distributions

```json
{
  "type": "chart",
  "props": {
    "chart_type": "line",  // line, bar, pie, area
    "title": "Monthly Sales",
    "data": [{"x": "Jan", "y": 100}, {"x": "Feb", "y": 150}]
  }
}
```

## Table Component

Best for: Detailed data, lists, records

```json
{
  "type": "table",
  "props": {
    "columns": [
      {"key": "name", "label": "Name"},
      {"key": "value", "label": "Value"}
    ],
    "rows": [
      {"name": "Item 1", "value": 100}
    ],
    "sortable": true
  }
}
```

## Choosing the Right Component

| Data Type | Best Component |
|-----------|---------------|
| Single number | metric |
| Time series | chart (line) |
| Categories | chart (bar/pie) |
| List of records | table |
| Status message | alert |
| Progress/loading | progress |
| User input | form |
""",
        },
        "best-practices": {
            "name": "Best Practices",
            "description": "UI design patterns and recommendations",
            "content": """# UI Best Practices

## Dashboard Design

1. **Lead with KPIs**: Put metrics at the top
2. **3-6 metrics max**: Don't overwhelm users
3. **Use grid layout**: 3 columns works well
4. **Charts below metrics**: For detailed trends
5. **Tables at bottom**: For drill-down data

## Component Guidelines

### Metrics
- Always include a label
- Use trends when comparing to previous period
- Keep values human-readable ($50K not $50000)

### Charts
- Choose chart type based on data:
  - Line: trends over time
  - Bar: category comparisons
  - Pie: proportions (max 5-6 slices)
- Always include a title
- Limit data points for readability

### Tables
- Limit columns to what's essential
- Enable sorting for large datasets
- Use pagination for 20+ rows

### Alerts
- Use appropriate severity:
  - info: neutral information
  - success: positive outcomes
  - warning: attention needed
  - error: problems/failures

## Layout Tips

- **Grid**: Best for dashboards, equal-sized items
- **Flex column**: Best for reports, sequential content
- **Flex row**: Best for side-by-side comparisons

## Accessibility

- Use descriptive labels
- Don't rely on color alone for meaning
- Provide text alternatives for charts
""",
        },
    }
