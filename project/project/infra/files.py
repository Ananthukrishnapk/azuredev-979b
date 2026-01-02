from pathlib import Path
from config import config


def setup_paths(config):
    """Resolve all relative paths to absolute paths based on project folder."""
    config.paths.temp_dir = config.paths.project_folder / config.paths.temp_dir
    config.paths.unlighthouse_reports = (
        config.paths.temp_dir / config.paths.unlighthouse_reports
    )
    config.paths.unlighthouse_artifacts = (
        config.paths.temp_dir / config.paths.unlighthouse_artifacts
    )
    return config


def ensure_dirs(cfg):
    """Ensure all required directories exist."""
    cfg.paths.temp_dir.mkdir(parents=True, exist_ok=True)
    cfg.paths.unlighthouse_reports.mkdir(parents=True, exist_ok=True)
    cfg.paths.unlighthouse_artifacts.mkdir(parents=True, exist_ok=True)


config = setup_paths(config)
ensure_dirs(config)

CONFIG = config
