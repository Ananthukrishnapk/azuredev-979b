from pathlib import Path
from types import SimpleNamespace

import yaml

# Load config.yml
config_path = Path(__file__).parent.parent / "config.yml"
with open(config_path, "r") as f:
    raw = yaml.safe_load(f)


def dict_to_namespace(d):
    """Recursively convert dict to SimpleNamespace for dot-access."""
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dict_to_namespace(v) for k, v in d.items()})
    return d


config = dict_to_namespace(raw)

# Set project folder path
config.paths.project_folder = Path(__file__).parent
