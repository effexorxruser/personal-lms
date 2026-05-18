from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
LEGACY_APP_ROOT = _APP_DIR.parent
REPO_ROOT = _APP_DIR.parents[2]
