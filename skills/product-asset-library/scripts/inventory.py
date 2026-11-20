"""List source files and stable content fingerprints as JSON, without editing the source."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat

MARKER = ".product-asset-library-output"
IGNORED = {".git", ".agents", ".codex", ".obsidian", "__pycache__", "node_modules"}
IGNORED_FILES = {".DS_Store", "AGENTS.md", "SKILL.md", "Thumbs.db"}

def inventory(folder):
    files = []
    errors = []
    def scan_error(error):
        errors.append({"path": os.path.relpath(error.filename, folder), "error": str(error.strerror)})
    for directory, dirs, names in os.walk(folder, onerror=scan_error):
        parent = Path(directory)
        if (parent / MARKER).is_file():
            dirs.clear()
            continue
        dirs[:] = sorted(d for d in dirs if d not in IGNORED and not (parent / d).is_symlink())
        for name in sorted(names):
            path = parent / name
            if name in IGNORED_FILES or name.startswith("._") or path.is_symlink():
                continue
            item = {"path": path.relative_to(folder).as_posix()}
            try:
                if not stat.S_ISREG(path.stat().st_mode):
                    continue
                digest = hashlib.sha256()
                with path.open("rb") as source:
                    for block in iter(lambda: source.read(1024 * 1024), b""):
                        digest.update(block)
                item["sha256"] = digest.hexdigest()
            except OSError as error:
                item["error"] = str(error.strerror)
            files.append(item)
    return {"files": files, "scan_errors": errors}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    folder = parser.parse_args().folder.expanduser().resolve()
    if not folder.is_dir():
        parser.error("请提供可读取的素材目录")
    print(json.dumps(inventory(folder), ensure_ascii=False, indent=2))
