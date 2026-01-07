# MCP Prompts

MCP Prompts provide structured templates that guide agents toward effective UI creation patterns. They encode best practices and common workflows into reusable prompt templates.

## Overview

Prompts help agents:

- **Follow** established UI patterns
- **Generate** consistent, well-structured views
- **Apply** best practices automatically
- **Reduce** trial-and-error in UI creation

## Available Prompts

### `create_dashboard`

Guides creation of a multi-panel dashboard.

**Arguments:**
- `title` (required): Dashboard title
- `metrics` (optional): List of metrics to display
- `charts` (optional): Chart configurations
- `refresh_interval` (optional): Auto-refresh interval in seconds

**Example:**
```
Create a dashboard titled "Sales Overview" with:
- Metrics: total_revenue, orders_today, conversion_rate
- Charts: revenue_trend (line), top_products (bar)
- Refresh every 30 seconds
```

### `add_visualization`

Guides adding a chart or visualization to an existing view.

**Arguments:**
- `view_id` (required): Target view ID
- `chart_type` (required): Type of chart (line, bar, pie, etc.)
- `data_source` (required): Data source identifier
- `title` (optional): Chart title

**Example:**
```
Add a line chart to view "dashboard-main" showing:
- Data source: sales_by_month
- Title: "Monthly Sales Trend"
```

### `design_form`

Guides creation of a data entry form.

**Arguments:**
- `purpose` (required): What the form is for
- `fields` (required): List of field definitions
- `validation` (optional): Validation rules
- `submit_action` (optional): Action on submit

**Example:**
```
Design a form for "New Customer Registration" with:
- Fields: name (text, required), email (email, required), phone (tel)
- Validation: email format, phone format
- Submit: POST to /api/customers
```

### `update_metrics`

Guides updating metric displays with new data.

**Arguments:**
- `view_id` (required): Target view ID
- `metrics` (required): Metric values to update
- `highlight_changes` (optional): Whether to animate changes

**Example:**
```
Update metrics in "dashboard-main":
- total_revenue: $125,430 (up 12%)
- orders_today: 47
- conversion_rate: 3.2%
Highlight changes with animations
```

### `create_status_page`

Guides creation of a system status page.

**Arguments:**
- `title` (required): Page title
- `services` (required): List of services to monitor
- `show_history` (optional): Whether to show incident history

**Example:**
```
Create a status page titled "System Health" monitoring:
- Services: API, Database, Cache, Queue
- Show 7-day incident history
```

## Using Prompts

Agents can use prompts to get structured guidance:

```python
# Agent workflow with prompts

# 1. Get the prompt template
prompt = await get_prompt("create_dashboard", {
    "title": "Sales Dashboard",
    "metrics": ["revenue", "orders", "customers"],
    "charts": [{"type": "line", "data": "sales_trend"}]
})

# 2. The prompt returns structured guidance
# that the agent can follow to create the dashboard

# 3. Agent makes tool calls based on prompt guidance
await call_tool("ui_create_view", {...})
await call_tool("ui_add_component", {...})
```

## Prompt Structure

Each prompt returns:

1. **Description**: What the prompt helps accomplish
2. **Steps**: Ordered steps to follow
3. **Tool Calls**: Suggested tool calls with parameters
4. **Validation**: How to verify success

## Benefits

1. **Consistency**: All dashboards follow the same patterns
2. **Best Practices**: Encoded expertise in templates
3. **Reduced Errors**: Structured guidance prevents mistakes
4. **Faster Development**: Skip the learning curve
