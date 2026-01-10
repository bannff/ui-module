"""View manager - orchestrates UI operations."""

import uuid
from datetime import datetime
from typing import Any

from .adapters.base import RenderAdapter, RenderResult
from .adapters.json_adapter import JsonAdapter
from .adapters.mcpui_adapter import McpUiAdapter
from .models import ComponentType, UIComponent, UIView, ViewUpdate
from .push_channel import PushChannel
from .registry import ComponentRegistry
from .store.view_store import InMemoryViewStore


class ViewManager:
    """Central manager for UI views and components.

    Orchestrates:
    - Component creation via registry
    - View persistence via store
    - Real-time updates via push channel
    - Rendering via adapters
    """

    def __init__(
        self,
        store: InMemoryViewStore | None = None,
        push_channel: PushChannel | None = None,
        registry: ComponentRegistry | None = None,
    ) -> None:
        self.store = store or InMemoryViewStore()
        self.push_channel = push_channel or PushChannel()
        self.registry = registry or ComponentRegistry()

        # Default adapters
        self._adapters: dict[str, RenderAdapter] = {
            "json": JsonAdapter(),
            "mcp-ui": McpUiAdapter(),
        }

    def register_adapter(self, adapter: RenderAdapter) -> None:
        """Register a render adapter."""
        self._adapters[adapter.adapter_type] = adapter

    def get_adapter(self, adapter_type: str) -> RenderAdapter | None:
        """Get a render adapter by type."""
        return self._adapters.get(adapter_type)

    def list_adapters(self) -> list[str]:
        """List available adapter types."""
        return list(self._adapters.keys())

    # View operations

    def create_view(
        self,
        name: str,
        view_id: str | None = None,
        layout: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UIView:
        """Create a new view."""
        view = UIView(
            id=view_id or str(uuid.uuid4()),
            name=name,
            layout=layout or {},
            metadata=metadata or {},
        )
        self.store.save(view)
        return view

    def get_view(self, view_id: str) -> UIView | None:
        """Get a view by ID."""
        return self.store.get(view_id)

    def delete_view(self, view_id: str) -> bool:
        """Delete a view."""
        return self.store.delete(view_id)

    def list_views(self) -> list[UIView]:
        """List all views."""
        return self.store.get_all()

    # Component operations

    def create_component(
        self,
        component_type: str | ComponentType,
        props: dict[str, Any] | None = None,
        styles: dict[str, str] | None = None,
        component_id: str | None = None,
    ) -> UIComponent:
        """Create a component using the registry."""
        if isinstance(component_type, str):
            component_type = ComponentType(component_type)

        return self.registry.create_component(
            component_id=component_id or str(uuid.uuid4()),
            component_type=component_type,
            props=props,
            styles=styles,
        )

    async def add_component(
        self,
        view_id: str,
        component: UIComponent,
        position: int | None = None,
    ) -> UIView | None:
        """Add a component to a view and push update."""
        view = self.store.get(view_id)
        if not view:
            return None

        if position is not None:
            view.components.insert(position, component)
        else:
            view.components.append(component)

        view.updated_at = datetime.utcnow()
        self.store.save(view)

        # Push update to clients
        update = ViewUpdate(
            view_id=view_id,
            action="add_component",
            payload={"component": component.to_dict(), "position": position},
            version=view.version,
        )
        self.store.record_update(update)
        await self.push_channel.push(update)

        return view

    async def update_component(
        self,
        view_id: str,
        component_id: str,
        props: dict[str, Any] | None = None,
        styles: dict[str, str] | None = None,
    ) -> UIComponent | None:
        """Update a component in a view."""
        view = self.store.get(view_id)
        if not view:
            return None

        component = None
        for c in view.components:
            if c.id == component_id:
                component = c
                break

        if not component:
            return None

        if props:
            component.props.update(props)
        if styles:
            component.styles.update(styles)
        component.updated_at = datetime.utcnow()

        view.updated_at = datetime.utcnow()
        self.store.save(view)

        # Push update
        update = ViewUpdate(
            view_id=view_id,
            action="update_component",
            payload={
                "component_id": component_id,
                "props": props,
                "styles": styles,
            },
            version=view.version,
        )
        self.store.record_update(update)
        await self.push_channel.push(update)

        return component

    async def remove_component(
        self,
        view_id: str,
        component_id: str,
    ) -> bool:
        """Remove a component from a view."""
        view = self.store.get(view_id)
        if not view:
            return False

        original_len = len(view.components)
        view.components = [c for c in view.components if c.id != component_id]

        if len(view.components) == original_len:
            return False

        view.updated_at = datetime.utcnow()
        self.store.save(view)

        # Push update
        update = ViewUpdate(
            view_id=view_id,
            action="remove_component",
            payload={"component_id": component_id},
            version=view.version,
        )
        self.store.record_update(update)
        await self.push_channel.push(update)

        return True

    async def push_view(self, view_id: str) -> int:
        """Push full view state to all subscribers."""
        view = self.store.get(view_id)
        if not view:
            return 0

        update = ViewUpdate(
            view_id=view_id,
            action="full",
            payload=view.to_dict(),
            version=view.version,
        )
        self.store.record_update(update)
        return await self.push_channel.push(update)

    # Rendering

    def render(
        self,
        view_id: str,
        adapter_type: str = "json",
    ) -> RenderResult | None:
        """Render a view using the specified adapter."""
        view = self.store.get(view_id)
        if not view:
            return None

        adapter = self._adapters.get(adapter_type)
        if not adapter:
            return None

        return adapter.render_view(view)

    def render_component(
        self,
        component: UIComponent,
        adapter_type: str = "json",
    ) -> RenderResult | None:
        """Render a single component."""
        adapter = self._adapters.get(adapter_type)
        if not adapter:
            return None
        return adapter.render_component(component)

    # State export

    def to_dict(self) -> dict[str, Any]:
        """Export manager state."""
        return {
            "views": self.store.to_dict(),
            "registry": self.registry.to_dict(),
            "push_channel": self.push_channel.to_dict(),
            "adapters": self.list_adapters(),
        }
