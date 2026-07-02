import difflib
from pathlib import Path

from . import ignore, mappings, renderer, state, templates


def _iter_bundle_files(bundle, paths):
    patterns = ignore.load_patterns(bundle)

    for target in paths:
        target_path = Path(target).expanduser().resolve()
        tpl_root = templates.template_root_for(bundle, target_path)

        if not tpl_root.exists():
            continue

        if tpl_root.is_file():
            if not ignore.is_ignored(Path(tpl_root.name), patterns):
                rel = tpl_root.relative_to(state.TEMPLATE_DIR)
                yield target_path, rel
            continue

        for tpl_file in sorted(tpl_root.rglob("*")):
            if not tpl_file.is_file():
                continue
            rel_to_root = tpl_file.relative_to(tpl_root)
            if ignore.is_ignored(rel_to_root, patterns):
                continue
            real_target = target_path / rel_to_root
            rel_to_template_dir = tpl_file.relative_to(state.TEMPLATE_DIR)
            yield real_target, rel_to_template_dir


def diff_file(target_path, rel_path, data):
    expected = renderer.render_template(rel_path, data)
    actual = target_path.read_text() if target_path.exists() else None

    if actual is None:
        status = "missing"
    elif actual == expected:
        status = "in-sync"
    else:
        status = "drift"

    diff_lines = list(
        difflib.unified_diff(
            (actual or "").splitlines(keepends=True),
            expected.splitlines(keepends=True),
            fromfile=str(target_path),
            tofile=f"{target_path} (rendered)",
        )
    )
    return status, diff_lines, expected


def diff_bundle(bundle, data=None):
    bundle_data = mappings.get_bundle(bundle)
    if bundle_data is None:
        raise ValueError(f"No such bundle: {bundle}")

    if data is None:
        data = state.load_state()

    results = []
    for target_path, rel_path in _iter_bundle_files(bundle, bundle_data["paths"]):
        status, diff_lines, expected = diff_file(target_path, rel_path, data)
        results.append((target_path, status, diff_lines, expected))
    return results
