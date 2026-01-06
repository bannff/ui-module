import os
from typing import Any, Dict, Optional
from mcp.server.fastmcp import FastMCP
from .engine.runtime import Runtime
from .engine.models import Envelope

# Initialize FastMCP
mcp = FastMCP("ui-module")

# Global runtime instance (lazy loaded or initialized via lifespan if FastMCP supported it,
# but for now we'll initialize it when running standardly or via a global)
runtime: Optional[Runtime] = None


def get_runtime() -> Runtime:
    global runtime
    if not runtime:
        # Default config path or from env
        import os

        config_dir = os.environ.get("UI_CONFIG_DIR", "./config")
        runtime = Runtime(config_dir)
    return runtime


# --- Deterministic Tools ---


@mcp.tool()
def get_capabilities() -> Dict[str, Any]:
    """
    Returns the capabilities of this UI engine.
    """
    return {
        "version": "0.1.0",
        "mode": "production",  # or debug
        "supported_components": [
            "container",
            "text",
            "button",
            "input",
            "form",
            "table",
            "card",
        ],
        "supports_server_driven_ui": True,
    }


@mcp.tool()
def get_sitemap() -> Dict[str, str]:
    """
    Returns the available routes mapping.
    """
    rt = get_runtime()
    return rt.router.routes


# --- Operational Tools ---


@mcp.tool()
def render_view(
    path: str,
    session_id: str,
    user_id: str = None,
    device_context: str = None,
    theme_preference: str = None,
) -> Dict[str, Any]:
    """
    Renders the view for a specific path.
    Args:
        path: The route to render (e.g., "/dashboard")
        session_id: Unique session identifier
        user_id: Optional user ID for personalization
        device_context: Optional device info (mobile, desktop)
        theme_preference: Optional theme (light, dark)
    """
    rt = get_runtime()
    envelope = Envelope(
        session_id=session_id,
        user_id=user_id,
        device_context=device_context,
        theme_preference=theme_preference,
    )
    try:
        return rt.render(path, envelope)
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def handle_event(
    event_id: str, payload: Dict[str, Any], session_id: str, user_id: str = None
) -> Dict[str, Any]:
    """
    Handles a UI event triggered by the client.
    """
    rt = get_runtime()
    envelope = Envelope(session_id=session_id, user_id=user_id)
    return rt.handle_event(event_id, payload, envelope)


@mcp.tool()
def get_session_state(session_id: str) -> Dict[str, Any]:
    """
    Retrieves the current state for a session.
    """
    rt = get_runtime()
    return rt.store.get_session(session_id).model_dump()


# --- Authoring Tools (Gated) ---
# Check env via os.environ for "UI_ENABLE_AUTHORING_TOOLS"
ENABLE_AUTHORING = os.environ.get("UI_ENABLE_AUTHORING_TOOLS") == "1"

if ENABLE_AUTHORING:

    @mcp.tool()
    def validate_view_definition(content: str) -> Dict[str, Any]:
        """
        Validates a YAML view definition string.
        """
        # Logic to parse YAML and validate against View model
        # For brevity, implementing basic check
        import yaml
        from .engine.models import View

        try:
            data = yaml.safe_load(content)
            View(**data)
            return {"valid": True}
        except Exception as e:
            return {"valid": False, "error": str(e)}
