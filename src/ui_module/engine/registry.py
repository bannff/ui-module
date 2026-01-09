"""Component registry for managing UI component definitions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from .models import ComponentType, UIComponent


@dataclass
class ComponentDefinition:
    """Definition of a registered component type."""

    component_type: ComponentType
    name: str
    description: str
    schema: dict[str, Any]  # JSON Schema for props validation
    default_props: dict[str, Any] = field(default_factory=dict)
    default_styles: dict[str, str] = field(default_factory=dict)
    validator: Callable[[dict[str, Any]], bool] | None = None
    registered_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.component_type.value,
            "name": self.name,
            "description": self.description,
            "schema": self.schema,
            "default_props": self.default_props,
            "default_styles": self.default_styles,
            "registered_at": self.registered_at.isoformat(),
        }


class ComponentRegistry:
    """Registry for UI component definitions.

    Manages available component types and their schemas,
    allowing agents to discover what UI primitives are available.
    """

    def __init__(self) -> None:
        self._components: dict[ComponentType, ComponentDefinition] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register built-in component types."""
        builtins = [
            ComponentDefinition(
                component_type=ComponentType.TEXT,
                name="Text",
                description="Display text content with optional formatting",
                schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "variant": {
                            "type": "string",
                            "enum": ["h1", "h2", "h3", "body", "caption"],
                        },
                    },
                    "required": ["content"],
                },
                default_props={"variant": "body"},
            ),
            ComponentDefinition(
                component_type=ComponentType.CHART,
                name="Chart",
                description="Display data visualizations (line, bar, pie, etc.)",
                schema={
                    "type": "object",
                    "properties": {
                        "chart_type": {
                            "type": "string",
                            "enum": ["line", "bar", "pie", "area", "scatter", "donut"],
                        },
                        "data": {"type": "array"},
                        "title": {"type": "string"},
                        "x_axis": {"type": "string"},
                        "y_axis": {"type": "string"},
                    },
                    "required": ["chart_type", "data"],
                },
                default_props={"chart_type": "line"},
            ),
            ComponentDefinition(
                component_type=ComponentType.TABLE,
                name="Table",
                description="Display tabular data with optional sorting/filtering",
                schema={
                    "type": "object",
                    "properties": {
                        "columns": {"type": "array", "items": {"type": "object"}},
                        "rows": {"type": "array", "items": {"type": "object"}},
                        "sortable": {"type": "boolean"},
                        "filterable": {"type": "boolean"},
                    },
                    "required": ["columns", "rows"],
                },
                default_props={"sortable": True, "filterable": False},
            ),
            ComponentDefinition(
                component_type=ComponentType.FORM,
                name="Form",
                description="Interactive form with input fields",
                schema={
                    "type": "object",
                    "properties": {
                        "fields": {"type": "array", "items": {"type": "object"}},
                        "submit_label": {"type": "string"},
                        "action": {"type": "string"},
                    },
                    "required": ["fields"],
                },
                default_props={"submit_label": "Submit"},
            ),
            ComponentDefinition(
                component_type=ComponentType.METRIC,
                name="Metric",
                description="Display a single metric/KPI with optional trend",
                schema={
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "value": {"type": ["string", "number"]},
                        "unit": {"type": "string"},
                        "trend": {"type": "string", "enum": ["up", "down", "flat"]},
                        "trend_value": {"type": "string"},
                    },
                    "required": ["label", "value"],
                },
            ),
            ComponentDefinition(
                component_type=ComponentType.CARD,
                name="Card",
                description="Container card with title and content",
                schema={
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "subtitle": {"type": "string"},
                        "content": {"type": "string"},
                    },
                },
            ),
            ComponentDefinition(
                component_type=ComponentType.ALERT,
                name="Alert",
                description="Display alert/notification message",
                schema={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "severity": {
                            "type": "string",
                            "enum": ["info", "success", "warning", "error"],
                        },
                        "dismissible": {"type": "boolean"},
                    },
                    "required": ["message"],
                },
                default_props={"severity": "info", "dismissible": True},
            ),
            ComponentDefinition(
                component_type=ComponentType.PROGRESS,
                name="Progress",
                description="Display progress indicator",
                schema={
                    "type": "object",
                    "properties": {
                        "value": {"type": "number", "minimum": 0, "maximum": 100},
                        "label": {"type": "string"},
                        "variant": {"type": "string", "enum": ["linear", "circular"]},
                    },
                    "required": ["value"],
                },
                default_props={"variant": "linear"},
            ),
        ]
        for defn in builtins:
            self._components[defn.component_type] = defn

    def register(self, definition: ComponentDefinition) -> None:
        """Register a component definition."""
        self._components[definition.component_type] = definition

    def get(self, component_type: ComponentType) -> ComponentDefinition | None:
        """Get a component definition."""
        return self._components.get(component_type)

    def list_components(self) -> list[ComponentDefinition]:
        """List all registered components."""
        return list(self._components.values())

    def create_component(
        self,
        component_id: str,
        component_type: ComponentType,
        props: dict[str, Any] | None = None,
        styles: dict[str, str] | None = None,
    ) -> UIComponent:
        """Create a component instance with defaults applied."""
        defn = self._components.get(component_type)
        merged_props = {}
        merged_styles = {}

        if defn:
            merged_props = {**defn.default_props}
            merged_styles = {**defn.default_styles}

        if props:
            merged_props.update(props)
        if styles:
            merged_styles.update(styles)

        return UIComponent(
            id=component_id,
            component_type=component_type,
            props=merged_props,
            styles=merged_styles,
        )

    def to_dict(self) -> dict[str, Any]:
        """Export registry as dictionary."""
        return {"components": [d.to_dict() for d in self._components.values()]}
