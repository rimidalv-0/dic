import fnmatch

from . import templates

IGNORE_FILENAME = ".dicignore"


def load_patterns(bundle):
    ignore_file = templates.bundle_dir(bundle) / IGNORE_FILENAME
    if not ignore_file.exists():
        return []

    patterns = []
    for line in ignore_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)
    return patterns


def is_ignored(rel_path, patterns):
    rel_posix = rel_path.as_posix()
    name = rel_path.name
    for pattern in patterns:
        if fnmatch.fnmatch(rel_posix, pattern) or fnmatch.fnmatch(name, pattern):
            return True
    return False
