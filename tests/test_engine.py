import unittest
import os
import shutil
import tempfile
import yaml
from ui_module.engine.runtime import Runtime
from ui_module.engine.models import Envelope

class TestEngine(unittest.TestCase):
    def setUp(self):
        # Create a temp config dir
        self.test_dir = tempfile.mkdtemp()
        self.config_dir = os.path.join(self.test_dir, "config")
        self.views_dir = os.path.join(self.config_dir, "views")
        os.makedirs(self.views_dir)
        
        # Create settings.yaml
        with open(os.path.join(self.config_dir, "settings.yaml"), "w") as f:
            yaml.dump({"routes": {"/": "index"}}, f)
            
        # Create index.yaml
        with open(os.path.join(self.views_dir, "index.yaml"), "w") as f:
            yaml.dump({
                "id": "index", 
                "layout": {
                    "type": "text", 
                    "props": {"content": "Hello {{ user.id }}"}
                }
            }, f)
            
        self.runtime = Runtime(self.config_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_render_view(self):
        envelope = Envelope(session_id="s1", user_id="u1")
        result = self.runtime.render("/", envelope)
        
        self.assertIn("layout", result)
        self.assertEqual(result["layout"]["id"], "index")
        self.assertEqual(result["layout"]["layout"]["props"]["content"], "Hello u1")

    def test_session_persistence(self):
        # Update session
        envelope = Envelope(session_id="s1")
        self.runtime.store.update_session("s1", data={"foo": "bar"})
        
        # Read back via runtime render context (implicitly tested) or direct store access
        state = self.runtime.store.get_session("s1")
        self.assertEqual(state.data["foo"], "bar")

if __name__ == "__main__":
    unittest.main()
