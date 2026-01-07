"""MCP Server for UI Module.

Provides tools for agent-driven UI manipulation:
- View management (create, read, update, delete)
- Component operations (add, update, remove)
- Real-time push to connected clients
- Multiple render adapters (JSON, MCP-UI)
"""

import os
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP

from .engine import (
    ViewManager,
    ComponentType,
    UIComponent,
    UIView,
)

logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    "ui-module",
    description="Agent-driven UI management with real-time push updates",
)

# Global view manager instance
_view_manager: ViewManager | None = None


def get_view_manager() -> ViewManager:
    """Get or create the view manager instance."""
    global _view_manager
    if _view_manager is None:
        _view_manager = ViewManager()
    return _view_manager


def is_authoring_enabled() -> bool:
    """Check if authoring tools are enabled."""
    return os.environ.get("AUTHORING_ENABLED", "false").lower() == "true"


# ============================================================================
# Query Tools - Always available
# ============================================================================

@mcp.tool()
def ui_list_views() -> dict[str, Any]:
    """List all available views.
    
    Returns a list of all views with their IDs, names, and component counts.
    """
    manager = get_view_manager()
    views = manager.list_views()
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
    }


@mcp.tool()
def ui_get_view(view_id: str, adapter: str = "json") -> dict[str, Any]:
    """Get a view by ID, optionally rendered through an adapter.
    
    Args:
        view_id: The view ID to retrieve
        adapter: Render adapter to use ("json" or "mcp-ui")
    
    Returns the view data rendered through the specified adapter.
    """
    manager = get_view_manager()
    result = manager.render(view_id, adapter_type=adapter)
    
    if not result:
        return {"error": f"View not found: {view_id}"}
    
    return result.to_dict()


@mcp.tool()
def ui_get_component_registry() -> dict[str, Any]:
    """Get the component registry showing available component types.
    
    Returns all registered component types with their schemas,
    so agents know what UI primitives are available.
    """
    manager = get_view_manager()
    return manager.registry.to_dict()


@mcp.tool()
def ui_get_push_channel_status() -> dict[str, Any]:
    """Get the status of the push channel.
    
    Shows connected clients and their subscriptions.
    """
    manager = get_view_manager()
    return manager.push_channel.to_dict()


@mcp.tool()
def ui_list_adapters() -> dict[str, Any]:
    """List available render adapters.
    
    Returns the adapter types that can be used for rendering views.
    """
    manager = get_view_manager()
    return {
        "adapters": manager.list_adapters(),
        "default": "json",
    }


@mcp.tool()
def ui_get_view_history(view_id: str | None = None, limit: int = 50) -> dict[str, Any]:
    """Get update history for views.
    
    Args:
        view_id: Optional view ID to filter history
        limit: Maximum number of updates to return
    
    Returns recent updates pushed to clients.
    """
    manager = get_view_manager()
    history = manager.store.get_history(view_id=view_id, limit=limit)
    return {
        "updates": [u.to_dict() for u in history],
        "count": len(history),
    }


# ============================================================================
# Authoring Tools - Require AUTHORING_ENABLED=true
# ============================================================================

@mcp.tool()
def ui_create_view(
    name: str,
    view_id: str | None = None,
    layout_type: str = "flex",
    layout_columns: int = 1,
) -> dict[str, Any]:
    """Create a new view.
    
    Args:
        name: Display name for the view
        view_id: Optional custom ID (auto-generated if not provided)
        layout_type: Layout type ("flex" or "grid")
        layout_columns: Number of columns for grid layout
    
    Returns the created view.
    Requires AUTHORING_ENABLED=true.
    """
    if not is_authoring_enabled():
        return {"error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true"}
    
    manager = get_view_manager()
    layout = {"type": layout_type}
    if layout_type == "grid":
        layout["columns"] = layout_columns
    
    view = manager.create_view(name=name, view_id=view_id, layout=layout)
    return {
        "created": True,
        "view": view.to_dict(),
    }


@mcp.tool()
def ui_delete_view(view_id: str) -> dict[str, Any]:
    """Delete a view.
    
    Args:
        view_id: The view ID to delete
    
    Requires AUTHORING_ENABLED=true.
    """
    if not is_authoring_enabled():
        return {"error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true"}
    
    manager = get_view_manager()
    deleted = manager.delete_view(view_id)
    return {
        "deleted": deleted,
        "view_id": view_id,
    }


@mcp.tool()
async def ui_add_component(
    view_id: str,
    component_type: str,
    props: dict[str, Any] | None = None,
    styles: dict[str, str] | None = None,
    component_id: str | None = None,
    position: int | None = None,
) -> dict[str, Any]:
    """Add a component to a view.
    
    Args:
        view_id: Target view ID
        component_type: Type of component (text, chart, table, metric, etc.)
        props: Component properties (varies by type)
        styles: CSS styles to apply
        component_id: Optional custom component ID
        position: Optional position in the component list
    
    The component is added and pushed to all subscribed clients.
    Requires AUTHORING_ENABLED=true.
    """
    if not is_authoring_enabled():
        return {"error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true"}
    
    manager = get_view_manager()
    
    try:
        component = manager.create_component(
            component_type=component_type,
            props=props,
            styles=styles,
            component_id=component_id,
        )
    except ValueError as e:
        return {"error": f"Invalid component type: {component_type}"}
    
    view = await manager.add_component(view_id, component, position)
    
    if not view:
        return {"error": f"View not found: {view_id}"}
    
    return {
        "added": True,
        "component": component.to_dict(),
        "view_version": view.version,
    }


@mcp.tool()
async def ui_update_component(
    view_id: str,
    component_id: str,
    props: dict[str, Any] | None = None,
    styles: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Update a component's properties or styles.
    
    Args:
        view_id: View containing the component
        component_id: Component to update
        props: Properties to update (merged with existing)
        styles: Styles to update (merged with existing)
    
    The update is pushed to all subscribed clients.
    Requires AUTHORING_ENABLED=true.
    """
    if not is_authoring_enabled():
        return {"error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true"}
    
    manager = get_view_manager()
    component = await manager.update_component(view_id, component_id, props, styles)
    
    if not component:
        return {"error": f"Component not found: {component_id} in view {view_id}"}
    
    return {
        "updated": True,
        "component": component.to_dict(),
    }


@mcp.tool()
async def ui_remove_component(view_id: str, component_id: str) -> dict[str, Any]:
    """Remove a component from a view.
    
    Args:
        view_id: View containing the component
        component_id: Component to remove
    
    The removal is pushed to all subscribed clients.
    Requires AUTHORING_ENABLED=true.
    """
    if not is_authoring_enabled():
        return {"error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true"}
    
    manager = get_view_manager()
    removed = await manager.remove_component(view_id, component_id)
    
    return {
        "removed": removed,
        "component_id": component_id,
        "view_id": view_id,
    }


@mcp.tool()
async def ui_push_view(view_id: str) -> dict[str, Any]:
    """Push full view state to all subscribed clients.
    
    Args:
        view_id: View to push
    
    Forces a full refresh of the view on all connected clients.
    Requires AUTHORING_ENABLED=true.
    """
    if not is_authoring_enabled():
        return {"error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true"}
    
    manager = get_view_manager()
    recipients = await manager.push_view(view_id)
    
    return {
        "pushed": True,
        "view_id": view_id,
        "recipients": recipients,
    }


@mcp.tool()
async def ui_create_dashboard(
    name: str,
    metrics: list[dict[str, Any]] | None = None,
    charts: list[dict[str, Any]] | None = None,
    tables: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Create a complete dashboard with multiple components.
    
    Args:
        name: Dashboard name
        metrics: List of metric configs [{label, value, unit, trend}]
        charts: List of chart configs [{title, chart_type, data}]
        tables: List of table configs [{columns, rows}]
    
    Convenience tool for creating a full dashboard in one call.
    Requires AUTHORING_ENABLED=true.
    """
    if not is_authoring_enabled():
        return {"error": "Authoring tools are disabled. Set AUTHORING_ENABLED=true"}
    
    manager = get_view_manager()
    
    # Create view with grid layout
    view = manager.create_view(
        name=name,
        layout={"type": "grid", "columns": 3},
    )
    
    components_added = []
    
    # Add metrics
    for metric in (metrics or []):
        component = manager.create_component(
            component_type=ComponentType.METRIC,
            props=metric,
        )
        await manager.add_component(view.id, component)
        components_added.append(component.id)
    
    # Add charts
    for chart in (charts or []):
        component = manager.create_component(
            component_type=ComponentType.CHART,
            props=chart,
        )
        await manager.add_component(view.id, component)
        components_added.append(component.id)
    
    # Add tables
    for table in (tables or []):
        component = manager.create_component(
            component_type=ComponentType.TABLE,
            props=table,
        )
        await manager.add_component(view.id, component)
        components_added.append(component.id)
    
    return {
        "created": True,
        "view_id": view.id,
        "view_name": name,
        "components_added": len(components_added),
        "component_ids": components_added,
    }


# ============================================================================
# Client Connection Tools
# ============================================================================

@mcp.tool()
def ui_connect_client(
    client_id: str,
    subscribe_to: list[str] | None = None,
) -> dict[str, Any]:
    """Register a client connection for receiving updates.
    
    Args:
        client_id: Unique identifier for the client
        subscribe_to: List of view IDs to subscribe to (use "*" for all)
    
    Returns connection details. The client should poll ui_get_client_updates
    or establish a WebSocket connection for real-time updates.
    """
    manager = get_view_manager()
    connection = manager.push_channel.connect(client_id)
    
    for view_id in (subscribe_to or []):
        manager.push_channel.subscribe(client_id, view_id)
    
    return {
        "connected": True,
        "client_id": client_id,
        "subscribed_to": list(connection.subscribed_views),
    }


@mcp.tool()
def ui_disconnect_client(client_id: str) -> dict[str, Any]:
    """Disconnect a client.
    
    Args:
        client_id: Client to disconnect
    """
    manager = get_view_manager()
    disconnected = manager.push_channel.disconnect(client_id)
    return {
        "disconnected": disconnected,
        "client_id": client_id,
    }


@mcp.tool()
def ui_subscribe(client_id: str, view_id: str) -> dict[str, Any]:
    """Subscribe a client to view updates.
    
    Args:
        client_id: Client to subscribe
        view_id: View to subscribe to (use "*" for all views)
    """
    manager = get_view_manager()
    subscribed = manager.push_channel.subscribe(client_id, view_id)
    return {
        "subscribed": subscribed,
        "client_id": client_id,
        "view_id": view_id,
    }


# ============================================================================
# Server entry point
# ============================================================================

def main():
    """Run the MCP server."""
    import asyncio
    mcp.run()


if __name__ == "__main__":
    main()
