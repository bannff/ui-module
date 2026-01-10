"""MCP Server for UI Module.

Provides tools, resources, and prompts for agent-driven UI manipulation:
- Deterministic tools (capabilities, health, schema)
- Operational tools (view/component CRUD with context envelope)
- Authoring tools (security-gated, config_dir scoped)
- Resources (component schemas, templates, docs)
- Prompts (guided UI creation patterns)
"""

import logging
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import prompts as prm
from . import resources as res
from .engine.envelope import ContextEnvelope
from .engine.models import ComponentType
from .engine.runtime import UIRuntime, get_runtime

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP("ui-module")


def _get_runtime() -> UIRuntime:
    """Get the runtime instance."""
    config_dir = os.environ.get("UI_CONFIG_DIR")
    return get_runtime(config_dir)


def _parse_envelope(envelope: dict[str, Any] | None) -> ContextEnvelope:
    """Parse context envelope from tool input."""
    return ContextEnvelope.from_dict(envelope)


# ============================================================================
# MCP Resources - Read-only data for agent context
# ============================================================================


@mcp.resource("ui://components")
def resource_all_components() -> str:
    """List all available UI component types with their schemas."""
    runtime = _get_runtime()
    assert runtime.view_manager is not None
    result = res.get_all_components_resource(runtime.view_manager.registry)
    return result["content"]


@mcp.resource("ui://components/{component_type}")
def resource_component_schema(component_type: str) -> str:
    """Get the JSON schema for a specific component type."""
    runtime = _get_runtime()
    assert runtime.view_manager is not None
    result = res.get_component_schema_resource(component_type, runtime.view_manager.registry)
    return result["content"]


@mcp.resource("ui://templates")
def resource_all_templates() -> str:
    """List all available view templates."""
    result = res.get_all_templates_resource()
    return result["content"]


@mcp.resource("ui://templates/{template_name}")
def resource_template(template_name: str) -> str:
    """Get a specific view template with layout and component suggestions."""
    result = res.get_template_resource(template_name)
    return result["content"]


@mcp.resource("ui://views/{view_id}")
def resource_view(view_id: str) -> str:
    """Get a specific view's current state."""
    runtime = _get_runtime()
    result = res.get_view_resource(view_id, runtime.view_manager)
    return result["content"]


@mcp.resource("ui://docs/{doc_name}")
def resource_docs(doc_name: str) -> str:
    """Get documentation content."""
    result = res.get_docs_resource(doc_name)
    return result["content"]


# ============================================================================
# MCP Prompts - Pre-built templates for common UI tasks
# ============================================================================


@mcp.prompt()
def create_dashboard(name: str, purpose: str, metrics: str = "", data: str = "") -> str:
    """Create a dashboard with metrics, charts, and tables.

    Args:
        name: Dashboard name
        purpose: What the dashboard is for
        metrics: List of KPIs to display
        data: Data to visualize
    """
    result = prm.get_prompt(
        "create_dashboard",
        {
            "name": name,
            "purpose": purpose,
            "metrics": metrics or "(not specified)",
            "data": data or "(not specified)",
        },
    )
    return result["messages"][0]["content"]["text"]


@mcp.prompt()
def add_visualization(view_id: str, data: str, title: str = "") -> str:
    """Add a data visualization to an existing view.

    Args:
        view_id: Target view ID
        data: Data to visualize (JSON)
        title: Chart title
    """
    result = prm.get_prompt(
        "add_visualization",
        {
            "view_id": view_id,
            "data": data,
            "title": title or "(auto-generate)",
        },
    )
    return result["messages"][0]["content"]["text"]


@mcp.prompt()
def design_form(purpose: str, fields: str) -> str:
    """Create a form for data collection.

    Args:
        purpose: What the form collects
        fields: Fields to include
    """
    result = prm.get_prompt(
        "design_form",
        {
            "purpose": purpose,
            "fields": fields,
        },
    )
    return result["messages"][0]["content"]["text"]


@mcp.prompt()
def update_metrics(view_id: str, updates: str) -> str:
    """Update multiple metrics on a dashboard.

    Args:
        view_id: Dashboard view ID
        updates: Metric updates (label -> new value)
    """
    result = prm.get_prompt(
        "update_metrics",
        {
            "view_id": view_id,
            "updates": updates,
        },
    )
    return result["messages"][0]["content"]["text"]


@mcp.prompt()
def create_status_page(name: str, systems: str) -> str:
    """Create a system status/health page.

    Args:
        name: Status page name
        systems: Systems to monitor
    """
    result = prm.get_prompt(
        "create_status_page",
        {
            "name": name,
            "systems": systems,
        },
    )
    return result["messages"][0]["content"]["text"]


# ============================================================================
# Deterministic Tools - Safe, testable, no side effects
# ============================================================================


@mcp.tool()
def ui_get_capabilities() -> dict[str, Any]:
    """Get module capabilities.

    Returns schema versions, supported adapters, authoring enabled flag,
    running mode, feature flags, and available component types.

    This is a deterministic tool - safe to call anytime.
    """
    runtime = _get_runtime()
    return runtime.get_capabilities()


@mcp.tool()
def ui_health_check() -> dict[str, Any]:
    """Check service health.

    Returns service status, store connectivity, push channel status,
    uptime, and last error (if any).

    This is a deterministic tool - safe to call anytime.
    """
    runtime = _get_runtime()
    return runtime.health_check()


@mcp.tool()
def ui_describe_config_schema() -> dict[str, Any]:
    """Get JSON schema for configuration.

    Returns the schema for settings.yaml and view definitions,
    useful for validation and documentation.

    This is a deterministic tool - safe to call anytime.
    """
    runtime = _get_runtime()
    return runtime.describe_config_schema()


@mcp.tool()
def ui_get_view_registry() -> dict[str, Any]:
    """Get sanitized list of loaded views.

    Returns view IDs, names, versions, component counts, and tags.
    Does not include sensitive data or full component details.

    This is a deterministic tool - safe to call anytime.
    """
    runtime = _get_runtime()
    return runtime.get_view_registry()


@mcp.tool()
def ui_get_component_registry() -> dict[str, Any]:
    """Get available component types and their schemas.

    Returns all registered component types with their JSON schemas,
    so agents know what UI primitives are available.

    This is a deterministic tool - safe to call anytime.
    """
    runtime = _get_runtime()
    if runtime.view_manager:
        return runtime.view_manager.registry.to_dict()
    return {"components": []}


@mcp.tool()
def ui_list_adapters() -> dict[str, Any]:
    """List available render adapters.

    Returns the adapter types that can be used for rendering views.

    This is a deterministic tool - safe to call anytime.
    """
    runtime = _get_runtime()
    if runtime.view_manager:
        return {
            "adapters": runtime.view_manager.list_adapters(),
            "default": runtime.settings.default_adapter if runtime.settings else "json",
        }
    return {"adapters": [], "default": "json"}


@mcp.tool()
def ui_list_resources() -> dict[str, Any]:
    """List all available MCP resources.

    Returns URIs for component schemas, templates, views, and documentation
    that agents can read for context.
    """
    runtime = _get_runtime()
    assert runtime.view_manager is not None
    resources = res.list_all_resources(runtime.view_manager.registry, runtime.view_manager)
    return {
        "resources": resources,
        "total": len(resources),
    }


@mcp.tool()
def ui_list_prompts() -> dict[str, Any]:
    """List all available MCP prompts.

    Returns prompt names and descriptions for guided UI creation.
    """
    prompts = prm.list_prompts()
    return {
        "prompts": prompts,
        "total": len(prompts),
    }


# ============================================================================
# Operational Tools - Stateful, idempotent, auditable
# All accept context envelope for cross-module composition
# ============================================================================


@mcp.tool()
def ui_list_views(envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    """List all available views.

    Args:
        envelope: Optional context envelope for correlation/audit

    Returns a list of all views with their IDs, names, and component counts.
    """
    ctx = _parse_envelope(envelope)
    runtime = _get_runtime()

    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    views = runtime.view_manager.list_views()
    return {
        "views": [
            {
                "id": v.id,
                "name": v.name,
                "component_count": len(v.components),
                "version": v.version,
                "updated_at": v.updated_at.isoformat(),
            }
            for v in views
        ],
        "total": len(views),
        "request_id": ctx.request_id,
    }


@mcp.tool()
def ui_get_view(
    view_id: str,
    adapter: str = "json",
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Get a view by ID, optionally rendered through an adapter.

    Args:
        view_id: The view ID to retrieve
        adapter: Render adapter to use ("json" or "mcp-ui")
        envelope: Optional context envelope for correlation/audit

    Returns the view data rendered through the specified adapter.
    """
    ctx = _parse_envelope(envelope)
    runtime = _get_runtime()

    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    result = runtime.view_manager.render(view_id, adapter_type=adapter)

    if not result:
        return {"error": f"View not found: {view_id}", "request_id": ctx.request_id}

    return {
        **result.to_dict(),
        "request_id": ctx.request_id,
    }


@mcp.tool()
def ui_get_push_channel_status(envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    """Get the status of the push channel.

    Args:
        envelope: Optional context envelope for correlation/audit

    Shows connected clients and their subscriptions.
    """
    ctx = _parse_envelope(envelope)
    runtime = _get_runtime()

    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    return {
        **runtime.view_manager.push_channel.to_dict(),
        "request_id": ctx.request_id,
    }


@mcp.tool()
def ui_get_view_history(
    view_id: str | None = None,
    limit: int = 50,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Get update history for views.

    Args:
        view_id: Optional view ID to filter history
        limit: Maximum number of updates to return
        envelope: Optional context envelope for correlation/audit

    Returns recent updates pushed to clients.
    """
    ctx = _parse_envelope(envelope)
    runtime = _get_runtime()

    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    history = runtime.view_manager.store.get_history(view_id=view_id, limit=limit)
    return {
        "updates": [u.to_dict() for u in history],
        "count": len(history),
        "request_id": ctx.request_id,
    }


@mcp.tool()
def ui_connect_client(
    client_id: str,
    subscribe_to: list[str] | None = None,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Register a client connection for receiving updates.

    Args:
        client_id: Unique identifier for the client
        subscribe_to: List of view IDs to subscribe to (use "*" for all)
        envelope: Optional context envelope for correlation/audit

    Returns connection details.
    """
    ctx = _parse_envelope(envelope)
    runtime = _get_runtime()

    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    connection = runtime.view_manager.push_channel.connect(client_id)

    for view_id in subscribe_to or []:
        runtime.view_manager.push_channel.subscribe(client_id, view_id)

    return {
        "connected": True,
        "client_id": client_id,
        "subscribed_to": list(connection.subscribed_views),
        "request_id": ctx.request_id,
    }


@mcp.tool()
def ui_disconnect_client(
    client_id: str,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Disconnect a client.

    Args:
        client_id: Client to disconnect
        envelope: Optional context envelope for correlation/audit
    """
    ctx = _parse_envelope(envelope)
    runtime = _get_runtime()

    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    disconnected = runtime.view_manager.push_channel.disconnect(client_id)
    return {
        "disconnected": disconnected,
        "client_id": client_id,
        "request_id": ctx.request_id,
    }


@mcp.tool()
def ui_subscribe(
    client_id: str,
    view_id: str,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Subscribe a client to view updates.

    Args:
        client_id: Client to subscribe
        view_id: View to subscribe to (use "*" for all views)
        envelope: Optional context envelope for correlation/audit
    """
    ctx = _parse_envelope(envelope)
    runtime = _get_runtime()

    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    subscribed = runtime.view_manager.push_channel.subscribe(client_id, view_id)
    return {
        "subscribed": subscribed,
        "client_id": client_id,
        "view_id": view_id,
        "request_id": ctx.request_id,
    }


# ============================================================================
# Authoring Tools - Security-gated, config_dir scoped
# Require AUTHORING_ENABLED=true or settings.authoring_enabled=true
# ============================================================================


def _is_authoring_enabled() -> bool:
    """Check if authoring tools are enabled."""
    if os.environ.get("AUTHORING_ENABLED", "").lower() == "true":
        return True
    runtime = _get_runtime()
    if runtime.settings and runtime.settings.authoring_enabled:
        return True
    return False


@mcp.tool()
def ui_authoring_get_status() -> dict[str, Any]:
    """Get authoring tools status.

    Returns enabled flag, config_dir, allowed paths, and schema versions.
    This tool is always available to check authoring status.
    """
    runtime = _get_runtime()
    return runtime.get_authoring_status()


@mcp.tool()
def ui_create_view(
    name: str,
    view_id: str | None = None,
    layout_type: str = "flex",
    layout_columns: int = 1,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a new view.

    Args:
        name: Display name for the view
        view_id: Optional custom ID (auto-generated if not provided)
        layout_type: Layout type ("flex" or "grid")
        layout_columns: Number of columns for grid layout
        envelope: Optional context envelope for correlation/audit

    Returns the created view. Requires AUTHORING_ENABLED=true.
    """
    ctx = _parse_envelope(envelope)

    if not _is_authoring_enabled():
        return {
            "error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true",
            "request_id": ctx.request_id,
        }

    runtime = _get_runtime()
    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    layout = {"type": layout_type}
    if layout_type == "grid":
        layout["columns"] = layout_columns  # type: ignore[assignment]

    view = runtime.view_manager.create_view(name=name, view_id=view_id, layout=layout)
    return {"created": True, "view": view.to_dict(), "request_id": ctx.request_id}


@mcp.tool()
def ui_delete_view(view_id: str, envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    """Delete a view. Requires AUTHORING_ENABLED=true."""
    ctx = _parse_envelope(envelope)

    if not _is_authoring_enabled():
        return {
            "error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true",
            "request_id": ctx.request_id,
        }

    runtime = _get_runtime()
    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    deleted = runtime.view_manager.delete_view(view_id)
    return {"deleted": deleted, "view_id": view_id, "request_id": ctx.request_id}


@mcp.tool()
async def ui_add_component(
    view_id: str,
    component_type: str,
    props: dict[str, Any] | None = None,
    styles: dict[str, str] | None = None,
    component_id: str | None = None,
    position: int | None = None,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Add a component to a view. Requires AUTHORING_ENABLED=true."""
    ctx = _parse_envelope(envelope)

    if not _is_authoring_enabled():
        return {
            "error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true",
            "request_id": ctx.request_id,
        }

    runtime = _get_runtime()
    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    try:
        component = runtime.view_manager.create_component(
            component_type=component_type,
            props=props,
            styles=styles,
            component_id=component_id,
        )
    except ValueError:
        return {"error": f"Invalid component type: {component_type}", "request_id": ctx.request_id}

    view = await runtime.view_manager.add_component(view_id, component, position)
    if not view:
        return {"error": f"View not found: {view_id}", "request_id": ctx.request_id}

    return {
        "added": True,
        "component": component.to_dict(),
        "view_version": view.version,
        "request_id": ctx.request_id,
    }


@mcp.tool()
async def ui_update_component(
    view_id: str,
    component_id: str,
    props: dict[str, Any] | None = None,
    styles: dict[str, str] | None = None,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Update a component's properties or styles. Requires AUTHORING_ENABLED=true."""
    ctx = _parse_envelope(envelope)

    if not _is_authoring_enabled():
        return {
            "error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true",
            "request_id": ctx.request_id,
        }

    runtime = _get_runtime()
    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    component = await runtime.view_manager.update_component(view_id, component_id, props, styles)
    if not component:
        return {
            "error": f"Component not found: {component_id} in view {view_id}",
            "request_id": ctx.request_id,
        }

    return {"updated": True, "component": component.to_dict(), "request_id": ctx.request_id}


@mcp.tool()
async def ui_remove_component(
    view_id: str, component_id: str, envelope: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Remove a component from a view. Requires AUTHORING_ENABLED=true."""
    ctx = _parse_envelope(envelope)

    if not _is_authoring_enabled():
        return {
            "error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true",
            "request_id": ctx.request_id,
        }

    runtime = _get_runtime()
    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    removed = await runtime.view_manager.remove_component(view_id, component_id)
    return {
        "removed": removed,
        "component_id": component_id,
        "view_id": view_id,
        "request_id": ctx.request_id,
    }


@mcp.tool()
async def ui_push_view(view_id: str, envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    """Push full view state to all subscribed clients. Requires AUTHORING_ENABLED=true."""
    ctx = _parse_envelope(envelope)

    if not _is_authoring_enabled():
        return {
            "error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true",
            "request_id": ctx.request_id,
        }

    runtime = _get_runtime()
    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    recipients = await runtime.view_manager.push_view(view_id)
    return {
        "pushed": True,
        "view_id": view_id,
        "recipients": recipients,
        "request_id": ctx.request_id,
    }


@mcp.tool()
async def ui_create_dashboard(
    name: str,
    metrics: list[dict[str, Any]] | None = None,
    charts: list[dict[str, Any]] | None = None,
    tables: list[dict[str, Any]] | None = None,
    envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a complete dashboard with multiple components. Requires AUTHORING_ENABLED=true."""
    ctx = _parse_envelope(envelope)

    if not _is_authoring_enabled():
        return {
            "error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true",
            "request_id": ctx.request_id,
        }

    runtime = _get_runtime()
    if not runtime.view_manager:
        return {"error": "Runtime not initialized", "request_id": ctx.request_id}

    view = runtime.view_manager.create_view(name=name, layout={"type": "grid", "columns": 3})
    components_added = []

    for metric in metrics or []:
        component = runtime.view_manager.create_component(
            component_type=ComponentType.METRIC, props=metric
        )
        await runtime.view_manager.add_component(view.id, component)
        components_added.append(component.id)

    for chart in charts or []:
        component = runtime.view_manager.create_component(
            component_type=ComponentType.CHART, props=chart
        )
        await runtime.view_manager.add_component(view.id, component)
        components_added.append(component.id)

    for table in tables or []:
        component = runtime.view_manager.create_component(
            component_type=ComponentType.TABLE, props=table
        )
        await runtime.view_manager.add_component(view.id, component)
        components_added.append(component.id)

    return {
        "created": True,
        "view_id": view.id,
        "view_name": name,
        "components_added": len(components_added),
        "component_ids": components_added,
        "request_id": ctx.request_id,
    }


# ============================================================================
# Server entry point
# ============================================================================


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
