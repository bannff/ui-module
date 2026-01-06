import pytest
import os
import shutil
import tempfile
import yaml
from ui_module.engine.runtime import Runtime


@pytest.fixture
def config_dir():
    temp_dir = tempfile.mkdtemp()
    config_path = os.path.join(temp_dir, "config")
    views_path = os.path.join(config_path, "views")
    os.makedirs(views_path)

    # Create settings.yaml
    with open(os.path.join(config_path, "settings.yaml"), "w") as f:
        yaml.dump({"routes": {"/": "index", "/login": "login"}}, f)

    yield config_path
    shutil.rmtree(temp_dir)


@pytest.fixture
def runtime(config_dir):
    return Runtime(config_dir)
