"""MCP-UI adapter for native MCP client rendering.

This adapter produces UIResource objects compatible with the MCP-UI protocol.
When MCP clients support MCP-UI, they can render these resources natively
within the chat interface.

See: https://mcpui.dev/
"""

from typing import Any
from enum import Enum

from .base import RenderAdapter, RenderResult
from ..models import UIView, UIComponent, ComponentType


class UIResourceType(str, Enum):
    """MCP-UI resource types."""
    INLINE_HTML = "inline_html"
    EXTERNAL_URL = "external_url"
    REMOTE_DOM = "remote_dom"


class McpUiAdapter(RenderAdapter):
    """Renders views as MCP-UI UIResource objects.
    
    This adapter produces output compatible with the MCP-UI protocol,
    allowing MCP clients that support it to render rich UI inline.
    
    Currently outputs inline HTML, but can be extended to support
    external URLs or remote-dom for more complex interactions.
    """

    def __init__(self, resource_type: UIResourceType = UIResourceType.INLINE_HTML) -> None:
        self._resource_type = resource_type

    @property
    def adapter_type(self) -> str:
        return "mcp-ui"

    @property
    def content_type(self) -> str:
        return "application/vnd.mcp-ui+json"

    def render_view(self, view: UIView) -> RenderResult:
        """Render view as MCP-UI UIResource."""
        html = self._view_to_html(view)
        
        ui_resource = {
            "type": self._resource_type.value,
            "content": html,
            "metadata": {
                "view_id": view.id,
                "view_name": view.name,
                "version": view.version,
            },
        }

        return RenderResult(
            adapter_type=self.adapter_type,
            content=ui_resource,
            content_type=self.content_type,
            metadata={
                "resource_type": self._resource_type.value,
                "component_count": len(view.components),
            },
        )

    def render_component(self, component: UIComponent) -> RenderResult:
        """Render component as MCP-UI UIResource."""
        html = self._component_to_html(component)
        
        ui_resource = {
            "type": self._resource_type.value,
            "content": html,
            "metadata": {
                "component_id": component.id,
                "component_type": component.component_type.value,
            },
        }

        return RenderResult(
            adapter_type=self.adapter_type,
            content=ui_resource,
            content_type=self.content_type,
        )

    def _view_to_html(self, view: UIView) -> str:
        """Convert view to HTML string."""
        components_html = "\n".join(
            self._component_to_html(c) for c in view.components
        )
        
        styles = self._generate_styles(view)
        
        return f"""<div class="mcp-ui-view" data-view-id="{view.id}">
  <style>{styles}</style>
  <div class="view-header">
    <h2>{view.name}</h2>
  </div>
  <div class="view-content" style="{self._layout_to_css(view.layout)}">
    {components_html}
  </div>
</div>"""

    def _component_to_html(self, component: UIComponent) -> str:
        """Convert component to HTML string."""
        renderer = self._get_component_renderer(component.component_type)
        return renderer(component)

    def _get_component_renderer(self, component_type: ComponentType):
        """Get the HTML renderer for a component type."""
        renderers = {
            ComponentType.TEXT: self._render_text,
            ComponentType.CHART: self._render_chart,
            ComponentType.TABLE: self._render_table,
            ComponentType.METRIC: self._render_metric,
            ComponentType.CARD: self._render_card,
            ComponentType.ALERT: self._render_alert,
            ComponentType.PROGRESS: self._render_progress,
            ComponentType.FORM: self._render_form,
            ComponentType.BUTTON: self._render_button,
            ComponentType.IMAGE: self._render_image,
            ComponentType.LIST: self._render_list,
        }
        return renderers.get(component_type, self._render_custom)

    def _render_text(self, c: UIComponent) -> str:
        variant = c.props.get("variant", "body")
        content = c.props.get("content", "")
        tag_map = {"h1": "h1", "h2": "h2", "h3": "h3", "body": "p", "caption": "span"}
        tag = tag_map.get(variant, "p")
        style = self._styles_to_css(c.styles)
        return f'<{tag} class="mcp-ui-text mcp-ui-text--{variant}" style="{style}">{content}</{tag}>'

    def _render_chart(self, c: UIComponent) -> str:
        # Charts would need JS library - output placeholder with data
        chart_type = c.props.get("chart_type", "line")
        title = c.props.get("title", "")
        data = c.props.get("data", [])
        return f"""<div class="mcp-ui-chart" data-chart-type="{chart_type}" data-component-id="{c.id}">
  <div class="chart-title">{title}</div>
  <div class="chart-placeholder">[{chart_type.upper()} CHART - {len(data)} data points]</div>
  <script type="application/json">{self._json_encode(data)}</script>
</div>"""

    def _render_table(self, c: UIComponent) -> str:
        columns = c.props.get("columns", [])
        rows = c.props.get("rows", [])
        
        header = "<tr>" + "".join(f"<th>{col.get('label', col.get('key', ''))}" for col in columns) + "</tr>"
        body_rows = []
        for row in rows:
            cells = "".join(f"<td>{row.get(col.get('key', ''), '')}" for col in columns)
            body_rows.append(f"<tr>{cells}</tr>")
        
        return f"""<table class="mcp-ui-table" data-component-id="{c.id}">
  <thead>{header}</thead>
  <tbody>{chr(10).join(body_rows)}</tbody>
</table>"""

    def _render_metric(self, c: UIComponent) -> str:
        label = c.props.get("label", "")
        value = c.props.get("value", "")
        unit = c.props.get("unit", "")
        trend = c.props.get("trend", "")
        trend_value = c.props.get("trend_value", "")
        
        trend_html = ""
        if trend:
            trend_icon = {"up": "↑", "down": "↓", "flat": "→"}.get(trend, "")
            trend_class = f"trend--{trend}"
            trend_html = f'<span class="metric-trend {trend_class}">{trend_icon} {trend_value}</span>'
        
        return f"""<div class="mcp-ui-metric" data-component-id="{c.id}">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{value}<span class="metric-unit">{unit}</span></div>
  {trend_html}
</div>"""

    def _render_card(self, c: UIComponent) -> str:
        title = c.props.get("title", "")
        subtitle = c.props.get("subtitle", "")
        content = c.props.get("content", "")
        
        children_html = "\n".join(self._component_to_html(child) for child in c.children)
        
        return f"""<div class="mcp-ui-card" data-component-id="{c.id}">
  <div class="card-header">
    <div class="card-title">{title}</div>
    <div class="card-subtitle">{subtitle}</div>
  </div>
  <div class="card-content">{content}{children_html}</div>
</div>"""

    def _render_alert(self, c: UIComponent) -> str:
        message = c.props.get("message", "")
        severity = c.props.get("severity", "info")
        return f'<div class="mcp-ui-alert mcp-ui-alert--{severity}" data-component-id="{c.id}">{message}</div>'

    def _render_progress(self, c: UIComponent) -> str:
        value = c.props.get("value", 0)
        label = c.props.get("label", "")
        variant = c.props.get("variant", "linear")
        
        if variant == "circular":
            return f"""<div class="mcp-ui-progress mcp-ui-progress--circular" data-component-id="{c.id}">
  <svg viewBox="0 0 36 36"><circle cx="18" cy="18" r="16" stroke-dasharray="{value}, 100"/></svg>
  <span class="progress-label">{label} {value}%</span>
</div>"""
        
        return f"""<div class="mcp-ui-progress mcp-ui-progress--linear" data-component-id="{c.id}">
  <div class="progress-label">{label}</div>
  <div class="progress-bar"><div class="progress-fill" style="width: {value}%"></div></div>
  <div class="progress-value">{value}%</div>
</div>"""

    def _render_form(self, c: UIComponent) -> str:
        fields = c.props.get("fields", [])
        submit_label = c.props.get("submit_label", "Submit")
        
        fields_html = []
        for field in fields:
            field_type = field.get("type", "text")
            name = field.get("name", "")
            label = field.get("label", name)
            fields_html.append(f"""<div class="form-field">
  <label for="{name}">{label}</label>
  <input type="{field_type}" name="{name}" id="{name}" />
</div>""")
        
        return f"""<form class="mcp-ui-form" data-component-id="{c.id}">
  {chr(10).join(fields_html)}
  <button type="submit">{submit_label}</button>
</form>"""

    def _render_button(self, c: UIComponent) -> str:
        label = c.props.get("label", "Button")
        variant = c.props.get("variant", "primary")
        return f'<button class="mcp-ui-button mcp-ui-button--{variant}" data-component-id="{c.id}">{label}</button>'

    def _render_image(self, c: UIComponent) -> str:
        src = c.props.get("src", "")
        alt = c.props.get("alt", "")
        return f'<img class="mcp-ui-image" src="{src}" alt="{alt}" data-component-id="{c.id}" />'

    def _render_list(self, c: UIComponent) -> str:
        items = c.props.get("items", [])
        ordered = c.props.get("ordered", False)
        tag = "ol" if ordered else "ul"
        items_html = "\n".join(f"<li>{item}</li>" for item in items)
        return f'<{tag} class="mcp-ui-list" data-component-id="{c.id}">{items_html}</{tag}>'

    def _render_custom(self, c: UIComponent) -> str:
        return f'<div class="mcp-ui-custom" data-component-id="{c.id}" data-type="{c.component_type.value}">{self._json_encode(c.props)}</div>'

    def _styles_to_css(self, styles: dict[str, str]) -> str:
        return "; ".join(f"{k}: {v}" for k, v in styles.items())

    def _layout_to_css(self, layout: dict[str, Any]) -> str:
        css_parts = []
        if layout.get("type") == "grid":
            cols = layout.get("columns", 1)
            css_parts.append(f"display: grid; grid-template-columns: repeat({cols}, 1fr); gap: 1rem")
        elif layout.get("type") == "flex":
            direction = layout.get("direction", "row")
            css_parts.append(f"display: flex; flex-direction: {direction}; gap: 1rem")
        return "; ".join(css_parts)

    def _generate_styles(self, view: UIView) -> str:
        return """
.mcp-ui-view { font-family: system-ui, sans-serif; padding: 1rem; }
.mcp-ui-metric { text-align: center; padding: 1rem; }
.mcp-ui-metric .metric-value { font-size: 2rem; font-weight: bold; }
.mcp-ui-metric .metric-label { color: #666; }
.mcp-ui-metric .trend--up { color: #22c55e; }
.mcp-ui-metric .trend--down { color: #ef4444; }
.mcp-ui-table { width: 100%; border-collapse: collapse; }
.mcp-ui-table th, .mcp-ui-table td { padding: 0.5rem; border: 1px solid #ddd; text-align: left; }
.mcp-ui-table th { background: #f5f5f5; }
.mcp-ui-card { border: 1px solid #ddd; border-radius: 8px; padding: 1rem; }
.mcp-ui-alert { padding: 1rem; border-radius: 4px; }
.mcp-ui-alert--info { background: #e0f2fe; color: #0369a1; }
.mcp-ui-alert--success { background: #dcfce7; color: #166534; }
.mcp-ui-alert--warning { background: #fef3c7; color: #92400e; }
.mcp-ui-alert--error { background: #fee2e2; color: #991b1b; }
.mcp-ui-progress--linear .progress-bar { background: #e5e5e5; height: 8px; border-radius: 4px; }
.mcp-ui-progress--linear .progress-fill { background: #3b82f6; height: 100%; border-radius: 4px; }
"""

    def _json_encode(self, data: Any) -> str:
        import json
        return json.dumps(data)
