"""Tests for MCP-UI adapter."""

from ui_module.engine import (
    ComponentType,
    McpUiAdapter,
    UIComponent,
    UIView,
)
from ui_module.engine.adapters.mcpui_adapter import UIResourceType


class TestMcpUiAdapter:
    """Tests for McpUiAdapter."""

    def test_adapter_type(self):
        """Should have correct adapter type."""
        adapter = McpUiAdapter()
        assert adapter.adapter_type == "mcp-ui"

    def test_content_type(self):
        """Should have correct content type."""
        adapter = McpUiAdapter()
        assert adapter.content_type == "application/vnd.mcp-ui+json"

    def test_render_view(self):
        """Should render view as UIResource."""
        adapter = McpUiAdapter()
        view = UIView(id="test", name="Test View")

        result = adapter.render_view(view)

        assert result.adapter_type == "mcp-ui"
        assert result.content["type"] == "inline_html"
        assert '<div class="mcp-ui-view"' in result.content["content"]

    def test_render_text_component(self):
        """Should render text component."""
        adapter = McpUiAdapter()
        component = UIComponent(
            id="text-1",
            component_type=ComponentType.TEXT,
            props={"content": "Hello World", "variant": "h1"},
        )

        result = adapter.render_component(component)

        assert "<h1" in result.content["content"]
        assert "Hello World" in result.content["content"]

    def test_render_metric_component(self):
        """Should render metric component."""
        adapter = McpUiAdapter()
        component = UIComponent(
            id="metric-1",
            component_type=ComponentType.METRIC,
            props={"label": "Revenue", "value": "$50,000", "trend": "up"},
        )

        result = adapter.render_component(component)
        content = result.content["content"]

        assert "mcp-ui-metric" in content
        assert "Revenue" in content
        assert "$50,000" in content
        assert "trend--up" in content

    def test_render_table_component(self):
        """Should render table component."""
        adapter = McpUiAdapter()
        component = UIComponent(
            id="table-1",
            component_type=ComponentType.TABLE,
            props={
                "columns": [{"key": "name", "label": "Name"}, {"key": "value", "label": "Value"}],
                "rows": [{"name": "Item 1", "value": 100}],
            },
        )

        result = adapter.render_component(component)
        content = result.content["content"]

        assert "<table" in content
        assert "<th>Name" in content
        assert "Item 1" in content

    def test_render_alert_component(self):
        """Should render alert with severity."""
        adapter = McpUiAdapter()
        component = UIComponent(
            id="alert-1",
            component_type=ComponentType.ALERT,
            props={"message": "Warning!", "severity": "warning"},
        )

        result = adapter.render_component(component)
        content = result.content["content"]

        assert "mcp-ui-alert--warning" in content
        assert "Warning!" in content

    def test_render_view_with_components(self):
        """Should render view with multiple components."""
        adapter = McpUiAdapter()
        view = UIView(
            id="dashboard",
            name="Dashboard",
            components=[
                UIComponent(
                    id="m1",
                    component_type=ComponentType.METRIC,
                    props={"label": "Users", "value": 100},
                ),
                UIComponent(
                    id="m2",
                    component_type=ComponentType.METRIC,
                    props={"label": "Sales", "value": 500},
                ),
            ],
        )

        result = adapter.render_view(view)
        content = result.content["content"]

        assert "Users" in content
        assert "Sales" in content
        assert result.metadata["component_count"] == 2

    def test_resource_type_configuration(self):
        """Should respect resource type configuration."""
        adapter = McpUiAdapter(resource_type=UIResourceType.INLINE_HTML)
        view = UIView(id="test", name="Test")

        result = adapter.render_view(view)

        assert result.content["type"] == "inline_html"
