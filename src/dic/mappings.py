import json

from . import state


def load_mappings():
    if not state.MAPPINGS_FILE.exists():
        return {}
    text = state.MAPPINGS_FILE.read_text().strip()
    if not text:
        return {}
    return json.loads(text)


def save_mappings(data):
    state.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    state.MAPPINGS_FILE.write_text(json.dumps(data, indent=2) + "\n")


def list_bundles():
    return load_mappings()


def get_bundle(bundle):
    return load_mappings().get(bundle)


def add_path(bundle, path):
    mappings = load_mappings()
    entry = mappings.setdefault(bundle, {"paths": []})
    if path not in entry["paths"]:
        entry["paths"].append(path)
    save_mappings(mappings)


def remove_bundle(bundle):
    mappings = load_mappings()
    if bundle not in mappings:
        return False
    del mappings[bundle]
    save_mappings(mappings)
    return True
