#!/usr/bin/env python3
"""Build a reproducible local plugin ZIP from explicit distribution resources."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import zipfile

# Reuse the installer's notice checks so source and standalone distributions
# accept the same format. Running the builder must not add payload caches.
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/kavazi-method/scripts"))
from onboarding import read_skill_license


def build(root: Path, output: Path) -> Path:
    root = root.resolve()
    manifest_path = root / "plugin.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError(f"Expected a regular distribution file: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("license") != "MIT":
        raise ValueError("Plugin manifest must declare license: MIT")
    for key in ("name", "version"):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise ValueError(f"Plugin manifest requires a nonempty {key}")
    files = [manifest_path] + [root / name for name in (
        "README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md",
    )]
    notice_path = root / "LICENSE"
    if notice_path.is_symlink() or not notice_path.is_file():
        raise ValueError(f"Expected a regular distribution file: {notice_path}")
    notice = notice_path.read_bytes()
    skills = root / "skills"
    if skills.is_symlink() or not skills.is_dir():
        raise ValueError(f"Expected a regular skills directory: {skills}")
    for name in ("kavazi-method", "kavazi-setup"):
        skill = skills / name
        if skill.is_symlink() or not skill.is_dir():
            raise ValueError(f"Missing required skill directory: {skill}")

    def walk_error(error: OSError) -> None:
        raise ValueError(f"Cannot inspect distribution directory: {error}") from error

    for skill in sorted(skills.iterdir()):
        if not skill.is_dir() or skill.is_symlink():
            raise ValueError(f"Expected a regular skill directory: {skill}")
        if skill.name == "__pycache__":
            continue
        if read_skill_license(skill) != notice:
            raise ValueError(f"Skill LICENSE must match the root LICENSE: {skill}")
        for directory, directories, names in os.walk(skill, followlinks=False, onerror=walk_error):
            directories.sort()
            for name in directories:
                path = Path(directory) / name
                if path.is_symlink():
                    raise ValueError(f"Symlinks are not distributable: {path}")
            directories[:] = [name for name in directories if name != "__pycache__"]
            for name in sorted(names):
                file = Path(directory) / name
                if file.is_symlink():
                    raise ValueError(f"Symlinks are not distributable: {file}")
                if file.name == "__pycache__" or file.suffix in {".pyc", ".pyo"}:
                    continue
                if not file.is_file():
                    raise ValueError(f"Expected a regular distribution file: {file}")
                files.append(file)
    output = output.absolute()
    if output.is_symlink():
        raise ValueError("Output cannot be a symlink")
    for parent in output.parents:
        if parent.is_symlink():
            raise ValueError("Output parent cannot be a symlink")
    # Reject symlink spellings first, then compare the actual normalized location.
    output = output.resolve(strict=False)
    if output.suffix.lower() != ".zip":
        raise ValueError("Output must have a .zip extension; source files are not archive destinations")
    if output in files or output.is_dir():
        raise ValueError("Output must be a ZIP path outside the source resources")
    if root / "skills" in output.parents:
        raise ValueError("Output must remain outside the skills payload")
    payload = []
    for file in sorted(files):
        if file.is_symlink() or not file.is_file():
            raise ValueError(f"Expected a regular distribution file: {file}")
        payload.append((file.relative_to(root).as_posix(), file.read_bytes()))
    output.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(output.stat().st_mode) if output.exists() else 0o644
    fd, temporary = tempfile.mkstemp(prefix=".kavazi-archive-", dir=output.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, content in payload:
                info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, content)
        os.chmod(temporary, mode)
        os.replace(temporary, output)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"Built {manifest['name']} {manifest['version']}: {output}")
    return output


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--output", type=Path, default=Path("dist/kavazi-method-0.1.0.zip"))
    args = arguments.parse_args()
    try:
        build(Path(__file__).resolve().parents[1], args.output)
    except (OSError, ValueError, KeyError) as error:
        arguments.exit(1, f"Build failed: {error}\n")
