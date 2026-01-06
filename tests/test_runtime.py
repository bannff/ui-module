import os
import yaml
from ui_module.engine.models import Envelope


def test_render_simple_view(runtime, config_dir):
    # Create a view
    with open(os.path.join(config_dir, "views", "index.yaml"), "w") as f:
        yaml.dump(
            {
                "id": "index",
                "layout": {"type": "text", "props": {"content": "Hello {{ user.id }}"}},
            },
            f,
        )

    envelope = Envelope(session_id="s1", user_id="alice")
    result = runtime.render("/", envelope)

    assert result["layout"]["id"] == "index"
    assert result["layout"]["layout"]["props"]["content"] == "Hello alice"
    assert result["state"]["current_path"] == "/"


def test_session_persistence(runtime):
    # Updated manually to test store persistence independently of render
    runtime.store.update_session("s_persistent", data={"counter": 1})

    state = runtime.store.get_session("s_persistent")
    assert state.data["counter"] == 1
