#!/usr/bin/env python3
"""Build the self-contained skill ZIP. Users only need an archive extractor."""
import argparse
import hashlib
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build(output, root=ROOT):
    root = Path(root)
    source = root / "skills/jstack-mode"
    files = {}
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Symlinks are not distributable: {path}")
        if not path.is_file():
            continue
        if path.suffix not in (".md", ".yaml"):
            raise ValueError(f"Unexpected skill artifact: {path}")
        files[path.relative_to(source).as_posix()] = path.read_bytes()
    if "SKILL.md" not in files:
        raise ValueError("Missing SKILL.md")
    # Check closure of local Markdown references inside the distributable folder.
    for name, data in files.items():
        if not name.endswith(".md"):
            continue
        for link in re.findall(r"\]\(([^)\s]+)\)", data.decode("utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = (source / name).parent / link.split("#", 1)[0]
            try:
                relative = target.resolve().relative_to(source.resolve()).as_posix()
            except ValueError as exc:
                raise ValueError(f"Reference escapes skill: {name} -> {link}") from exc
            if relative not in files:
                raise ValueError(f"Missing bundled reference: {name} -> {link}")
    files["LICENSE"] = (root / "LICENSE").read_bytes()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "jstack-mode.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo("jstack-mode/" + name, date_time=(2026, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(info, data)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(f"{checksum}  {archive.name}\n", encoding="utf-8")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    print(build(args.output))


if __name__ == "__main__":
    main()
