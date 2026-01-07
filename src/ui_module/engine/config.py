"""Configuration management for UI module.

Supports config_dir pattern for portable, config-driven behavior.
"""

import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from .models import UIView, UIComponent, ComponentType

logger = logging.getLogger(__name__)


@dataclass
class UISettings:
    """UI module settings loaded from config/settings.yaml."""
    # Authoring
    authoring_enabled: bool = False
    
    # Push channel
    push_enabled: bool = True
    max_clients: int = 100
    
    # Storage
    storage_backend: str = "memory"  # memory, redis, filesystem
    storage_path: str | None = None
    
    # Adapters
    default_adapter: str = "json"
    enabled_adapters: list[str] = field(default_factory=lambda: ["json", "mcp-ui"])
    
    # Limits
    max_views: int = 1000
    max_components_per_view: int = 100
    max_history_entries: int = 1000
    
    # Feature flags
    feature_flags: dict[str, bool] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UISettings":
        """Create from dictionary."""
        return cls(
            authoring_enabled=data.get("authoring_enabled", False),
            push_enabled=data.get("push_enabled", True),
            max_clients=data.get("max_clients", 100),
            storage_backend=data.get("storage_backend", "memory"),
            storage_path=data.get("storage_path"),
            default_adapter=data.get("default_adapter", "json"),
            enabled_adapters=data.get("enabled_adapters", ["json", "mcp-ui"]),
            max_views=data.get("max_views", 1000),
            max_components_per_view=data.get("max_components_per_view", 100),
            max_history_entries=data.get("max_history_entries", 1000),
            feature_flags=data.get("feature_flags", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "authoring_enabled": self.authoring_enabled,
            "push_enabled": self.push_enabled,
            "max_clients": self.max_clients,
            "storage_backend": self.storage_backend,
            "storage_path": self.storage_path,
            "default_adapter": self.default_adapter,
            "enabled_adapters": self.enabled_adapters,
            "max_views": self.max_views,
            "max_components_per_view": self.max_components_per_view,
            "max_history_entries": self.max_history_entries,
            "feature_flags": self.feature_flags,
        }


@dataclass
class ViewDefinition:
    """A view definition loaded from config/views/*.yaml."""
    id: str
    name: str
    description: str = ""
    layout: dict[str, Any] = field(default_factory=dict)
    components: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    def to_view(self) -> UIView:
        """Convert to UIView instance."""
        components = []
        for i, comp_def in enumerate(self.components):
            component = UIComponent(
                id=comp_def.get("id", f"{self.id}-comp-{i}"),
                component_type=ComponentType(comp_def.get("type", "text")),
                props=comp_def.get("props", {}),
                styles=comp_def.get("styles", {}),
            )
            components.append(component)
        
        return UIView(
            id=self.id,
            name=self.name,
            components=components,
            layout=self.layout,
            metadata={**self.metadata, "description": self.description, "tags": self.tags},
        )


class ConfigLoader:
    """Loads configuration from config_dir.
    
    Expected structure:
        config_dir/
            settings.yaml
            views/
                dashboard.yaml
                reports.yaml
    """

    def __init__(self, config_dir: str | Path | None = None):
        self.config_dir = Path(config_dir) if config_dir else self._default_config_dir()
        self._settings: UISettings | None = None
        self._view_definitions: dict[str, ViewDefinition] = {}

    def _default_config_dir(self) -> Path:
        """Get default config directory."""
        # Check environment variable first
        env_dir = os.environ.get("UI_CONFIG_DIR")
        if env_dir:
            return Path(env_dir)
        
        # Default to ./config
        return Path("./config")

    def _validate_path(self, path: Path) -> None:
        """Validate path is within config_dir (traversal protection)."""
        try:
            resolved = path.resolve()
            config_resolved = self.config_dir.resolve()
            if not str(resolved).startswith(str(config_resolved)):
                raise ValueError(f"Path traversal detected: {path}")
        except Exception as e:
            raise ValueError(f"Invalid path: {path}") from e

    def load_settings(self) -> UISettings:
        """Load settings from config/settings.yaml."""
        if self._settings:
            return self._settings
        
        settings_path = self.config_dir / "settings.yaml"
        
        if not settings_path.exists():
            logger.info(f"No settings.yaml found at {settings_path}, using defaults")
            self._settings = UISettings()
            return self._settings
        
        self._validate_path(settings_path)
        
        with open(settings_path) as f:
            data = yaml.safe_load(f) or {}
        
        # Override with environment variables
        if os.environ.get("AUTHORING_ENABLED", "").lower() == "true":
            data["authoring_enabled"] = True
        
        self._settings = UISettings.from_dict(data)
        logger.info(f"Loaded settings from {settings_path}")
        return self._settings

    def load_view_definitions(self) -> dict[str, ViewDefinition]:
        """Load view definitions from config/views/*.yaml."""
        if self._view_definitions:
            return self._view_definitions
        
        views_dir = self.config_dir / "views"
        
        if not views_dir.exists():
            logger.info(f"No views directory at {views_dir}")
            return {}
        
        self._validate_path(views_dir)
        
        for yaml_file in views_dir.glob("*.yaml"):
            self._validate_path(yaml_file)
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f) or {}
                
                view_id = data.get("id", yaml_file.stem)
                definition = ViewDefinition(
                    id=view_id,
                    name=data.get("name", view_id),
                    description=data.get("description", ""),
                    layout=data.get("layout", {}),
                    components=data.get("components", []),
                    metadata=data.get("metadata", {}),
                    tags=data.get("tags", []),
                )
                self._view_definitions[view_id] = definition
                logger.debug(f"Loaded view definition: {view_id}")
            except Exception as e:
                logger.error(f"Failed to load view from {yaml_file}: {e}")
        
        logger.info(f"Loaded {len(self._view_definitions)} view definitions")
        return self._view_definitions

    def reload(self) -> None:
        """Reload all configuration."""
        self._settings = None
        self._view_definitions = {}
        self.load_settings()
        self.load_view_definitions()

    def get_config_schema(self) -> dict[str, Any]:
        """Get JSON schema for configuration."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "UI Module Configuration",
            "type": "object",
            "properties": {
                "settings": {
                    "type": "object",
                    "properties": {
                        "authoring_enabled": {"type": "boolean", "default": False},
                        "push_enabled": {"type": "boolean", "default": True},
                        "max_clients": {"type": "integer", "default": 100},
                        "storage_backend": {"type": "string", "enum": ["memory", "redis", "filesystem"]},
                        "storage_path": {"type": "string"},
                        "default_adapter": {"type": "string", "default": "json"},
                        "enabled_adapters": {"type": "array", "items": {"type": "string"}},
                        "max_views": {"type": "integer", "default": 1000},
                        "max_components_per_view": {"type": "integer", "default": 100},
                        "max_history_entries": {"type": "integer", "default": 1000},
                        "feature_flags": {"type": "object", "additionalProperties": {"type": "boolean"}},
                    },
                },
                "view_definition": {
                    "type": "object",
                    "required": ["id", "name"],
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "layout": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["flex", "grid"]},
                                "columns": {"type": "integer"},
                                "direction": {"type": "string"},
                            },
                        },
                        "components": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["type"],
                                "properties": {
                                    "id": {"type": "string"},
                                    "type": {"type": "string"},
                                    "props": {"type": "object"},
                                    "styles": {"type": "object"},
                                },
                            },
                        },
                        "metadata": {"type": "object"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        }
