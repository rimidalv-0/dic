from pathlib import Path

from . import state


def path_to_template_subpath(path):
    path = Path(path).expanduser().resolve()
    home = Path.home().resolve()
    try:
        return path.relative_to(home)
    except ValueError:
        return path.relative_to(path.anchor)


def bundle_dir(bundle):
    return state.TEMPLATE_DIR / bundle


def template_root_for(bundle, target_path):
    return bundle_dir(bundle) / path_to_template_subpath(target_path)
