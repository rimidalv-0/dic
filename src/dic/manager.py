import os
import shutil
import subprocess
from pathlib import Path

from . import diff as diff_mod
from . import ignore, mappings, renderer, state, sync as sync_mod, templates


def _copy_into_templates(src, dest):
    try:
        text = src.read_text()
    except (UnicodeDecodeError, ValueError):
        shutil.copy2(src, dest)
        return
    dest.write_text(renderer.escape_literal_braces(text))
    shutil.copystat(src, dest)


def _require_init():
    if not state.CONFIG_DIR.exists():
        raise SystemExit("[dic] not initialized, run `dic init` first")


def _bundle_names(bundle):
    if bundle:
        if mappings.get_bundle(bundle) is None:
            raise SystemExit(f"[dic] no such bundle: {bundle}")
        return [bundle]
    return list(mappings.list_bundles().keys())


def init():
    state.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    state.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
    if not state.STATE_FILE.exists():
        state.save_state({})
    if not state.MAPPINGS_FILE.exists():
        mappings.save_mappings({})
    print(f"[dic] initialized {state.CONFIG_DIR}")


def add(bundle, path):
    _require_init()
    source = Path(path).expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"[dic] path does not exist: {source}")

    dest = templates.template_root_for(bundle, source)
    patterns = ignore.load_patterns(bundle)

    if source.is_file():
        dest.parent.mkdir(parents=True, exist_ok=True)
        _copy_into_templates(source, dest)
    else:
        for f in sorted(source.rglob("*")):
            if not f.is_file():
                continue
            rel = f.relative_to(source)
            if ignore.is_ignored(rel, patterns):
                continue
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            _copy_into_templates(f, out)

    mappings.add_path(bundle, str(source))
    print(f"[dic] added {source} -> {bundle} ({dest})")


def remove(bundle):
    _require_init()
    if mappings.remove_bundle(bundle):
        print(f"[dic] removed bundle {bundle} (templates kept on disk)")
    else:
        print(f"[dic] no such bundle: {bundle}")


def list_bundles():
    _require_init()
    bundles = mappings.list_bundles()
    if not bundles:
        print("[dic] no bundles registered")
    for name, entry in bundles.items():
        print(name)
        for p in entry["paths"]:
            print(f"  {p}")
    return bundles


def status(bundle=None):
    _require_init()
    summary = {}
    for name in _bundle_names(bundle):
        results = diff_mod.diff_bundle(name)
        counts = {"in-sync": 0, "drift": 0, "missing": 0}
        for _, s, _, _ in results:
            counts[s] += 1
        summary[name] = counts
        paths = mappings.get_bundle(name)["paths"]
        print(
            f"{name}: {len(paths)} path(s), {counts['in-sync']} in-sync, "
            f"{counts['drift']} drift, {counts['missing']} missing"
        )
    return summary


def render(bundle=None):
    _require_init()
    rendered = {}
    for name in _bundle_names(bundle):
        results = diff_mod.diff_bundle(name)
        rendered[name] = [(target_path, expected) for target_path, _, _, expected in results]
        for target_path, _, _, expected in results:
            print(f"\n--- {target_path} ---")
            print(expected)
    return rendered


def diff(bundle=None):
    _require_init()
    all_results = {}
    for name in _bundle_names(bundle):
        results = diff_mod.diff_bundle(name)
        all_results[name] = results
        for target_path, s, diff_lines, _ in results:
            if s == "in-sync":
                continue
            print(f"\n--- {target_path} ({s}) ---")
            print("".join(diff_lines))
    return all_results


def sync(bundle=None):
    _require_init()
    for name in _bundle_names(bundle):
        sync_mod.sync_bundle(name)


def edit(bundle):
    _require_init()
    target = templates.bundle_dir(bundle)
    if not target.exists():
        raise SystemExit(f"[dic] no templates for bundle: {bundle}")
    editor = os.environ.get("EDITOR", "vi")
    subprocess.run([editor, str(target)])
