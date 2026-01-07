"""UI Module engine exports."""

from .models import (
    ComponentType,
    ChartType,
    ComponentConfig,
    UIComponent,
    UIView,
    ViewUpdate,
    ViewStore,
)
from .registry import ComponentRegistry, ComponentDefinition
from .store.view_store import InMemoryViewStore
from .push_channel import PushChannel, ClientConnection, ChannelType
from .view_manager import ViewManager
from .adapters import RenderAdapter, RenderResult, JsonAdapter, McpUiAdapter

__all__ = [
    # Models
    "ComponentType",
    "ChartType",
    "ComponentConfig",
    "UIComponent",
    "UIView",
    "ViewUpdate",
    "ViewStore",
    # Registry
    "ComponentRegistry",
    "ComponentDefinition",
    # Store
    "InMemoryViewStore",
    # Push
    "PushChannel",
    "ClientConnection",
    "ChannelType",
    # Manager
    "ViewManager",
    # Adapters
    "RenderAdapter",
    "RenderResult",
    "JsonAdapter",
    "McpUiAdapter",
]
