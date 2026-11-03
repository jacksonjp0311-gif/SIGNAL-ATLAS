#!/usr/bin/env python3
"""Validate and package an immutable numbered Signal Atlas archive."""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path

from release_files import iter_release_files

ROOT = Path(__file__).resolve().parents[1]

VALIDATORS = {
    "v0.5": ["validate.py", "validate_science.py", "validate_v05.py"],
    "v0.6": ["validate.py", "validate_science.py", "validate_v06.py"],
    "v0.7": ["validate.py", "validate_science.py", "validate_v07.py"],
    "v0.8": ["validate.py", "validate_science.py", "validate_v08.py"],
    "v1.0": ["validate.py", "validate_science.py", "validate_v10.py"],
}


def run(*arguments: str) -> None:
    subprocess.check_call([sys.executable, "-B", *arguments], cwd=ROOT)


def manifest_entries() -> list[tuple[str, str]]:
    entries = []
    for path in sorted(iter_release_files(ROOT)):
        if path.name == "MANIFEST.sha256":
            continue
        relative = path.relative_to(ROOT).as_posix()
        entries.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
    return entries


def verify_archive(output: Path, entries: list[tuple[str, str]]) -> int:
    expected = {f"SIGNAL-ATLAS/{relative}": digest for relative, digest in entries}
    expected["SIGNAL-ATLAS/MANIFEST.sha256"] = ""
    with zipfile.ZipFile(output) as archive:
        bad_member = archive.testzip()
        if bad_member is not None:
            raise RuntimeError(f"ZIP CRC check failed for {bad_member}")
        actual_names = set(archive.namelist())
        if actual_names != set(expected):
            missing = sorted(set(expected) - actual_names)
            extra = sorted(actual_names - set(expected))
            raise RuntimeError(f"Archive contents differ from manifest; missing={missing[:5]} extra={extra[:5]}")
        for name, digest in expected.items():
            if not digest:
                continue
            actual = hashlib.sha256(archive.read(name)).hexdigest()
            if actual != digest:
                raise RuntimeError(f"Archive content hash mismatch for {name}")
    return len(expected)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", default="v1.0", choices=tuple(VALIDATORS))
    parser.add_argument("--output", type=Path, help="output ZIP; defaults beside this project tree")
    args = parser.parse_args()
    output = (args.output or ROOT.parent / f"SIGNAL-ATLAS-{args.version}.zip").resolve()
    if output.exists():
        raise SystemExit(f"Output already exists, version ZIPs are immutable: {output}")
    try:
        output.relative_to(ROOT)
    except ValueError:
        pass
    else:
        raise SystemExit("Output ZIP must be outside the project tree")

    if args.version == "v0.7":
        run(str(ROOT / "tools" / "build_space_weather_v07.py"))
    elif args.version == "v0.8":
        run(str(ROOT / "tools" / "build_rtsw_v08.py"))
    elif args.version == "v1.0":
        run(str(ROOT / "tools" / "build_v10.py"))

    for script in VALIDATORS[args.version]:
        run(str(ROOT / "tools" / script))

    if args.version == "v0.7":
        run("-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", "test_v07_space_weather.py")
    elif args.version == "v0.8":
        run("-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", "test_v08_solar_wind.py")
    elif args.version == "v1.0":
        run("-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", "test_v10_atlas.py")

    entries = manifest_entries()
    (ROOT / "MANIFEST.sha256").write_text(
        "".join(f"{digest}  {relative}\n" for relative, digest in entries),
        encoding="utf-8",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(iter_release_files(ROOT)):
            archive.write(path, arcname="SIGNAL-ATLAS/" + path.relative_to(ROOT).as_posix())

    members = verify_archive(output, entries)
    print(
        "RELEASE",
        args.version,
        "ZIP",
        output,
        "files",
        members,
        "SHA256",
        hashlib.sha256(output.read_bytes()).hexdigest(),
    )


if __name__ == "__main__":
    main()
