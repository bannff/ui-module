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
from .envelope import ContextEnvelope
from .config import ConfigLoader, UISettings, ViewDefinition
from .registry import ComponentRegistry, ComponentDefinition
from .store.view_store import InMemoryViewStore
from .push_channel import PushChannel, ClientConnection, ChannelType
from .view_manager import ViewManager
from .runtime import UIRuntime, get_runtime, reset_runtime
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
    # Envelope
    "ContextEnvelope",
    # Config
    "ConfigLoader",
    "UISettings",
    "ViewDefinition",
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
    # Runtime
    "UIRuntime",
    "get_runtime",
    "reset_runtime",
    # Adapters
    "RenderAdapter",
    "RenderResult",
    "JsonAdapter",
    "McpUiAdapter",
]
