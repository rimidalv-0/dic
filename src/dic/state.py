import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "dic"
STATE_FILE = CONFIG_DIR / "state.json"
MAPPINGS_FILE = CONFIG_DIR / "mappings.json"
TEMPLATE_DIR = CONFIG_DIR / "templates"


def load_state():
    if not STATE_FILE.exists():
        return {}
    text = STATE_FILE.read_text().strip()
    if not text:
        return {}
    return json.loads(text)


def save_state(data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(data, indent=2) + "\n")
