"""MCP Prompts for UI Module.

Prompts provide pre-built templates that guide agents toward
effective UI creation patterns.
"""

from typing import Any


def get_prompt(prompt_name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Get a prompt by name with arguments filled in."""
    prompts = _get_prompts()

    if prompt_name not in prompts:
        return {
            "name": prompt_name,
            "error": f"Unknown prompt: {prompt_name}",
        }

    prompt = prompts[prompt_name]
    content = prompt["template"]

    # Fill in arguments
    if arguments:
        for key, value in arguments.items():
            placeholder = "{" + key + "}"
            if isinstance(value, (list, dict)):
                import json

                value = json.dumps(value, indent=2)
            content = content.replace(placeholder, str(value))

    return {
        "name": prompt_name,
        "description": prompt["description"],
        "messages": [
            {
                "role": "user",
                "content": {"type": "text", "text": content},
            }
        ],
    }


def list_prompts() -> list[dict[str, Any]]:
    """List all available prompts."""
    prompts = _get_prompts()
    return [
        {
            "name": name,
            "description": prompt["description"],
            "arguments": prompt.get("arguments", []),
        }
        for name, prompt in prompts.items()
    ]


def _get_prompts() -> dict[str, dict[str, Any]]:
    """Get all prompt definitions."""
    return {
        "create_dashboard": {
            "description": "Create a dashboard with metrics, charts, and tables",
            "arguments": [
                {"name": "name", "description": "Dashboard name", "required": True},
                {"name": "purpose", "description": "What the dashboard is for", "required": True},
                {"name": "metrics", "description": "List of KPIs to display", "required": False},
                {"name": "data", "description": "Data to visualize", "required": False},
            ],
            "template": """Create a dashboard with the following requirements:

**Name**: {name}
**Purpose**: {purpose}

**Metrics to display**:
{metrics}

**Data to visualize**:
{data}

## Instructions

1. First, read the `ui://templates/dashboard` resource to understand the recommended layout
2. Read `ui://components` to see available component types and their schemas
3. Use `ui_create_view` to create the dashboard with a grid layout (3 columns)
4. Add metric components at the top for KPIs
5. Add chart components for data visualization
6. Add table components if detailed data is needed

## Best Practices

- Use 3-6 metrics maximum
- Choose chart types based on data:
  - Time series → line chart
  - Categories → bar chart
  - Proportions → pie chart
- Include trends on metrics when comparing periods
- Use human-readable values ($50K not $50000)
""",
        },
        "add_visualization": {
            "description": "Add a data visualization to an existing view",
            "arguments": [
                {"name": "view_id", "description": "Target view ID", "required": True},
                {"name": "data", "description": "Data to visualize", "required": True},
                {"name": "title", "description": "Chart title", "required": False},
            ],
            "template": """Add a visualization to view `{view_id}` for this data:

```json
{data}
```

**Title**: {title}

## Instructions

1. Analyze the data structure to determine the best chart type:
   - Time series data (dates/timestamps) → line chart
   - Category comparisons → bar chart
   - Part-to-whole relationships → pie chart (max 5-6 slices)
   - Correlation between variables → scatter chart
   - Cumulative values → area chart

2. Read `ui://components/chart` for the chart component schema

3. Use `ui_add_component` with:
   - `component_type`: "chart"
   - `props.chart_type`: chosen type
   - `props.title`: descriptive title
   - `props.data`: formatted data array

4. Consider adding axis labels if the data has clear dimensions
""",
        },
        "design_form": {
            "description": "Create a form for data collection",
            "arguments": [
                {"name": "purpose", "description": "What the form collects", "required": True},
                {"name": "fields", "description": "Fields to include", "required": True},
            ],
            "template": """Create a form for: {purpose}

**Fields needed**:
{fields}

## Instructions

1. Read `ui://templates/form` for the recommended form layout
2. Read `ui://components/form` for the form component schema

3. Create a view with flex column layout:
   ```
   ui_create_view(name="...", layout_type="flex")
   ```

4. Add a title using text component with variant "h2"

5. Add the form component with appropriate field types:
   - Text input: `{"type": "text", "name": "...", "label": "..."}`
   - Email: `{"type": "email", ...}`
   - Number: `{"type": "number", ...}`
   - Long text: `{"type": "textarea", ...}`
   - Selection: `{"type": "select", "options": [...], ...}`
   - Checkbox: `{"type": "checkbox", ...}`

6. Use clear, descriptive labels for each field

7. Consider adding an alert component for validation feedback
""",
        },
        "update_metrics": {
            "description": "Update multiple metrics on a dashboard",
            "arguments": [
                {"name": "view_id", "description": "Dashboard view ID", "required": True},
                {
                    "name": "updates",
                    "description": "Metric updates (label → new value)",
                    "required": True,
                },
            ],
            "template": """Update metrics on dashboard `{view_id}` with new values:

{updates}

## Instructions

1. First, get the current view to find component IDs:
   ```
   ui_get_view(view_id="{view_id}")
   ```

2. For each metric to update, use `ui_update_component`:
   ```
   ui_update_component(
       view_id="{view_id}",
       component_id="<component_id>",
       props={{"value": "<new_value>"}}
   )
   ```

3. If updating trends, include trend data:
   ```
   props={{"value": "$55,000", "trend": "up", "trend_value": "+10%"}}
   ```

4. Updates are pushed to connected clients automatically

## Tips

- Only include props that are changing (they merge with existing)
- Use human-readable values
- Update trends to reflect period-over-period changes
""",
        },
        "create_status_page": {
            "description": "Create a system status/health page",
            "arguments": [
                {"name": "name", "description": "Status page name", "required": True},
                {"name": "systems", "description": "Systems to monitor", "required": True},
            ],
            "template": """Create a status page for monitoring:

**Name**: {name}

**Systems to monitor**:
{systems}

## Instructions

1. Read `ui://templates/status` for the recommended layout

2. Create a view with grid layout (2 columns):
   ```
   ui_create_view(name="{name}", layout_type="grid", layout_columns=2)
   ```

3. Add a title with text component (h1 variant)

4. For each system, add:
   - An alert component showing current status:
     - severity "success" for healthy
     - severity "warning" for degraded
     - severity "error" for down

5. Add metric components for key health indicators:
   - Uptime percentage
   - Response time
   - Error rate
   - etc.

6. Optionally add progress components for resource usage:
   - CPU usage
   - Memory usage
   - Disk usage

## Status Severity Guide

- `success` (green): System healthy, all checks passing
- `info` (blue): Informational, no action needed
- `warning` (yellow): Degraded performance, attention needed
- `error` (red): System down or critical issue
""",
        },
    }
