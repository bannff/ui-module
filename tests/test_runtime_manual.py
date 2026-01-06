import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from ui_module.engine.runtime import Runtime
from ui_module.engine.models import Envelope

def main():
    config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../config"))
    print(f"Initializing Runtime with config: {config_dir}")
    
    runtime = Runtime(config_dir)
    
    envelope = Envelope(session_id="test-session-1", user_id="user-123")
    
    print("\n--- Rendering Dashboard (/) ---")
    result = runtime.render("/", envelope)
    print(json.dumps(result, indent=2))
    
    print("\n--- Rendering Login (/login) ---")
    result = runtime.render("/login", envelope)
    print(json.dumps(result, indent=2))

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    main()
