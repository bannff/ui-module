from typing import Dict, Any
import yaml
import os
from .models import Envelope
from .router import Router
from .renderer import Renderer
from .store.memory_store import MemoryStore


class Runtime:
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.store = MemoryStore()

        # Load settings to get routes
        settings_path = os.path.join(config_dir, "settings.yaml")
        routes = {}
        if os.path.exists(settings_path):
            with open(settings_path, "r") as f:
                settings = yaml.safe_load(f) or {}
                routes = settings.get("routes", {})

        self.router = Router(routes)
        self.renderer = Renderer(config_dir)

    def render(self, path: str, envelope: Envelope) -> Dict[str, Any]:
        """
        Renders a view for a given path and session.
        Returns: { "layout": ..., "state": ... }
        """
        # 1. Resolve Path -> View ID
        view_id = self.router.resolve(path)
        if not view_id:
            raise FileNotFoundError(f"No view found for path: {path}")

        # 2. Get/Link Session
        session = self.store.get_session(envelope.session_id)

        # 3. Update Session Path
        self.store.update_session(envelope.session_id, current_path=path)

        # 4. Prepare Context (Global State + Session State + Envelope)
        context = {
            "session": session.data,
            "user": {"id": envelope.user_id} if envelope.user_id else {},
            "device": envelope.device_context,
            "theme": envelope.theme_preference,
        }

        # 5. Render View
        view = self.renderer.render_view(view_id, context)

        return {"layout": view.model_dump(), "state": session.model_dump()}

    def handle_event(
        self, event_id: str, payload: Dict[str, Any], envelope: Envelope
    ) -> Dict[str, Any]:
        """
        Handles a UI event.
        Current implementation is simple: it just echoes; in real world it would run specific handlers.
        """
        session = self.store.get_session(envelope.session_id)

        # Logic to process event would go here.
        # For now, we update state if payload contains 'set_state'
        if "set_state" in payload:
            self.store.update_session(envelope.session_id, data=payload["set_state"])
            session = self.store.get_session(envelope.session_id)

        return {
            "effect": "update",  # or "navigate"
            "new_state": session.model_dump(),
        }
