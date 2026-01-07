"""Runtime orchestrator for UI module.

Loads configuration, initializes components, and provides
the main entry point for the module.
"""

import logging
from pathlib import Path
from typing import Any
from datetime import datetime

from .config import ConfigLoader, UISettings
from .models import UIView
from .registry import ComponentRegistry
from .store.view_store import InMemoryViewStore
from .push_channel import PushChannel
from .view_manager import ViewManager
from .adapters import JsonAdapter, McpUiAdapter

logger = logging.getLogger(__name__)

# Module version
__version__ = "0.2.0"
SCHEMA_VERSION = "1.0.0"


class UIRuntime:
    """Main runtime for UI module.
    
    Orchestrates configuration loading, component initialization,
    and provides the unified interface for the MCP server.
    """

    def __init__(self, config_dir: str | Path | None = None):
        self.config_loader = ConfigLoader(config_dir)
        self.settings: UISettings | None = None
        self.view_manager: ViewManager | None = None
        self._initialized = False
        self._started_at: datetime | None = None
        self._last_error: str | None = None
        self._running_mode = "stdio"  # stdio, http, lambda

    def initialize(self) -> None:
        """Initialize the runtime."""
        if self._initialized:
            return
        
        try:
            # Load settings
            self.settings = self.config_loader.load_settings()
            
            # Initialize components
            registry = ComponentRegistry()
            store = InMemoryViewStore()
            push_channel = PushChannel()
            
            # Create view manager
            self.view_manager = ViewManager(
                store=store,
                push_channel=push_channel,
                registry=registry,
            )
            
            # Register adapters based on settings
            if "json" in self.settings.enabled_adapters:
                self.view_manager.register_adapter(JsonAdapter())
            if "mcp-ui" in self.settings.enabled_adapters:
                self.view_manager.register_adapter(McpUiAdapter())
            
            # Load view definitions from config
            view_definitions = self.config_loader.load_view_definitions()
            for view_def in view_definitions.values():
                view = view_def.to_view()
                self.view_manager.store.save(view)
                logger.info(f"Loaded view from config: {view.id}")
            
            self._initialized = True
            self._started_at = datetime.utcnow()
            logger.info("UI Runtime initialized")
            
        except Exception as e:
            self._last_error = str(e)
            logger.error(f"Failed to initialize runtime: {e}")
            raise

    def get_capabilities(self) -> dict[str, Any]:
        """Get module capabilities.
        
        Returns schema versions, supported backends, feature flags, etc.
        """
        self._ensure_initialized()
        
        return {
            "module": "ui-module",
            "version": __version__,
            "schema_version": SCHEMA_VERSION,
            "running_mode": self._running_mode,
            "authoring_enabled": self.settings.authoring_enabled if self.settings else False,
            "adapters": {
                "available": self.view_manager.list_adapters() if self.view_manager else [],
                "default": self.settings.default_adapter if self.settings else "json",
            },
            "storage": {
                "backend": self.settings.storage_backend if self.settings else "memory",
            },
            "push": {
                "enabled": self.settings.push_enabled if self.settings else True,
                "max_clients": self.settings.max_clients if self.settings else 100,
            },
            "limits": {
                "max_views": self.settings.max_views if self.settings else 1000,
                "max_components_per_view": self.settings.max_components_per_view if self.settings else 100,
            },
            "feature_flags": self.settings.feature_flags if self.settings else {},
            "component_types": [
                c.component_type.value 
                for c in (self.view_manager.registry.list_components() if self.view_manager else [])
            ],
        }

    def health_check(self) -> dict[str, Any]:
        """Check service health.
        
        Returns status, connectivity, uptime, and any errors.
        """
        status = "healthy"
        checks = {}
        
        # Check initialization
        if not self._initialized:
            status = "unhealthy"
            checks["initialized"] = False
        else:
            checks["initialized"] = True
        
        # Check store connectivity
        try:
            if self.view_manager:
                view_count = len(self.view_manager.store.list_views())
                checks["store"] = {"status": "ok", "view_count": view_count}
            else:
                checks["store"] = {"status": "not_initialized"}
                status = "degraded"
        except Exception as e:
            checks["store"] = {"status": "error", "error": str(e)}
            status = "unhealthy"
        
        # Check push channel
        try:
            if self.view_manager:
                client_count = len(self.view_manager.push_channel.list_clients())
                checks["push_channel"] = {"status": "ok", "connected_clients": client_count}
            else:
                checks["push_channel"] = {"status": "not_initialized"}
        except Exception as e:
            checks["push_channel"] = {"status": "error", "error": str(e)}
            status = "degraded"
        
        # Calculate uptime
        uptime_seconds = None
        if self._started_at:
            uptime_seconds = (datetime.utcnow() - self._started_at).total_seconds()
        
        return {
            "status": status,
            "checks": checks,
            "uptime_seconds": uptime_seconds,
            "started_at": self._started_at.isoformat() if self._started_at else None,
            "last_error": self._last_error,
        }

    def describe_config_schema(self) -> dict[str, Any]:
        """Get JSON schema for configuration.
        
        Returns the schema for settings.yaml and view definitions.
        """
        return self.config_loader.get_config_schema()

    def get_view_registry(self) -> dict[str, Any]:
        """Get sanitized list of loaded views.
        
        Returns view metadata without sensitive data.
        """
        self._ensure_initialized()
        
        views = []
        if self.view_manager:
            for view in self.view_manager.list_views():
                views.append({
                    "id": view.id,
                    "name": view.name,
                    "version": view.version,
                    "component_count": len(view.components),
                    "tags": view.metadata.get("tags", []),
                    "updated_at": view.updated_at.isoformat(),
                })
        
        return {
            "views": views,
            "total": len(views),
            "config_dir": str(self.config_loader.config_dir),
        }

    def get_authoring_status(self) -> dict[str, Any]:
        """Get authoring tools status.
        
        Returns enabled flag, config_dir, allowed paths, etc.
        """
        return {
            "enabled": self.settings.authoring_enabled if self.settings else False,
            "config_dir": str(self.config_loader.config_dir),
            "views_dir": str(self.config_loader.config_dir / "views"),
            "schema_version": SCHEMA_VERSION,
        }

    def _ensure_initialized(self) -> None:
        """Ensure runtime is initialized."""
        if not self._initialized:
            self.initialize()


# Global runtime instance
_runtime: UIRuntime | None = None


def get_runtime(config_dir: str | Path | None = None) -> UIRuntime:
    """Get or create the global runtime instance."""
    global _runtime
    if _runtime is None:
        _runtime = UIRuntime(config_dir)
        _runtime.initialize()
    return _runtime


def reset_runtime() -> None:
    """Reset the global runtime (for testing)."""
    global _runtime
    _runtime = None
