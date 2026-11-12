"""Read the single release version and render Windows executable metadata."""

from __future__ import annotations

from pathlib import Path
import re
import sys


VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+")


def read_version(version_file: Path | None = None) -> str:
    if version_file is None:
        root = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
        version_file = root / "VERSION"
    value = Path(version_file).read_text(encoding="utf-8").strip()
    if not VERSION_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid VERSION value: {value!r}; expected major.minor.patch")
    return value


def render_version_resource(template: str, release_version: str) -> str:
    if not VERSION_PATTERN.fullmatch(release_version):
        raise ValueError(f"Invalid release version: {release_version!r}")
    parts = tuple(int(part) for part in release_version.split(".")) + (0,)
    if template.count("{{VERSION_TUPLE}}") != 2 or template.count("{{VERSION}}") != 2:
        raise ValueError("Windows version resource template is incomplete")
    return template.replace("{{VERSION_TUPLE}}", repr(parts)).replace("{{VERSION}}", release_version)
